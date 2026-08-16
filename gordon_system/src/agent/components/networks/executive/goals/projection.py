# Executive Goal Projections
# ==========================

"""
Executive Goal Projection - Immutable dataclass describing a goal projection.

A goal projection represents a goal reference along with all metadata about its
semantic organization, lifecycle state, and relationship to the current program.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# GOAL KINDS - Typed semantic categories of goals
# =============================================================================

class GoalKind(Enum):
    """
    Typed categories of goals.
    
    These represent the semantic nature of what is desired, not how it's achieved.
    """
    
    # State-oriented goals
    ACHIEVE_STATE = "achieve_state"
    """Desired new state or condition."""
    
    MAINTAIN_STATE = "maintain_state"
    """Required ongoing state preservation."""
    
    AVOID_STATE = "avoid_state"
    """Condition to be prevented or avoided."""
    
    RESTORE_STATE = "restore_state"
    """Return system to a known good state."""
    
    # Outcome-oriented goals
    PRODUCE_ARTIFACT = "produce_artifact"
    """Creation of a specific artifact or output."""
    
    ANSWER_QUESTION = "answer_question"
    """Resolution of an information need."""
    
    MAKE_DECISION = "make_decision"
    """Reach a decision about a course of action."""
    
    COMPLETE_TASK = "complete_task"
    """Completion of a bounded task."""
    
    VERIFY_CLAIM = "verify_claim"
    """Verification or falsification of a claim."""
    
    RESOLVE_CONFLICT = "resolve_conflict"
    """Resolution of competing requirements or evidence."""
    
    SATISFY_CONSTRAINT = "satisfy_constraint"
    """Compliance with an explicit constraint."""
    
    # Relationship-oriented goals
    FULFILL_COMMITMENT = "fulfill_commitment"
    """Carry out a binding obligation."""
    
    MONITOR_CONDITION = "monitor_condition"
    """Ongoing observation of a condition or metric."""
    
    PRESERVE_CONTINUITY = "preserve_continuity"
    """Maintain ongoing process or relationship."""
    
    REDUCE_UNCERTAINTY = "reduce_uncertainty"
    """Decrease epistemic uncertainty about a proposition."""
    
    IMPROVE_PERFORMANCE = "improve_performance"
    """Enhance system or process performance."""
    
    RECOVER_OPERATION = "recover_operation"
    """Restore operations after failure or degradation."""
    
    COMMUNICATE_RESULT = "communicate_result"
    """Deliver information to another agent or system."""
    
    # General
    GENERAL = "general"
    """General-purpose goal with unspecified kind."""
    
    UNKNOWN = "unknown"
    """Goal kind is unknown or unclassified."""


# =============================================================================
# GOAL STATUS - Lifecycle states of goals
# =============================================================================

class GoalStatus(Enum):
    """
    Semantic lifecycle status of a goal.
    
    These are semantic states, NOT process or scheduler states:
        PROPOSED: Proposed but not yet accepted
        ACCEPTED: Accepted into the program's organization
        ACTIVE: Currently being pursued
        PAUSED: Temporarily suspended by executive decision
        SUSPENDED: Suspended due to dependency or priority
        BLOCKED: Blocked by unmet dependencies
        WAITING: Waiting for external result or authority decision
        PARTIALLY_SATISFIED: Some criteria met but not complete
        SATISFIED: All satisfaction criteria met
        FAILED: Satisfaction impossible with current strategy
        ABANDONED: Executive decision to stop pursuing
        TERMINATED: Terminated by authority decision
        EXPIRED: Time or event bound expired
        SUPERSEDED: Replaced by a new goal
        REJECTED: Not accepted into organization
    """
    
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    PAUSED = "paused"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    WAITING = "waiting"
    PARTIALLY_SATISFIED = "partially_satisfied"
    SATISFIED = "satisfied"
    FAILED = "failed"
    ABANDONED = "abandoned"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


# =============================================================================
# GOAL ACTIVATION STATE - Executive network's view of activation
# =============================================================================

class GoalActivationState(Enum):
    """
    Executive Network's view of goal activation.
    
    This is distinct from:
        - Goal acceptance (semantic organization)
        - Goal priority (relative claim on resources)
        - Current focus (attentional allocation)
        - Execution progression (runtime state)
    """
    
    INACTIVE = "inactive"
    """Goal is not currently active in the program."""
    
    ELIGIBLE = "eligible"
    """Goal meets criteria for activation but not yet selected."""
    
    PROPOSED_FOR_ACTIVATION = "proposed_for_activation"
    """Executive has proposed activating this goal."""
    
    ACTIVE = "active"
    """Goal is actively being pursued."""
    
    PROPOSED_FOR_SUSPENSION = "proposed_for_suspension"
    """Executive has proposed suspending this goal."""
    
    SUSPENDED = "suspended"
    """Goal is suspended (may resume later)."""
    
    PROPOSED_FOR_REACTIVATION = "proposed_for_reactivation"
    """Executive has proposed reactivating a suspended goal."""
    
    PROPOSED_FOR_TERMINATION = "proposed_for_termination"
    """Executive has proposed terminating this goal."""
    
    TERMINAL = "terminal"
    """Goal has reached a terminal state (satisfied/failed/abandoned)."""


# =============================================================================
# GOAL OWNER REFERENCE - Reference to external owner
# =============================================================================

@dataclass(frozen=True)
class GoalOwnerReference:
    """
    Reference to the owner of an externally owned goal.
    
    The Executive Network does NOT own source goals. It only holds references
    to them and metadata about their relationship to the current program.
    """
    
    owner_id: str = "unknown_owner"
    """Identifier for the owning system or agent."""
    
    owner_type: str = "external"
    """Type of owner (e.g., 'user', 'system', 'policy')."""
    
    authority_reference_id: Optional[str] = None
    """Reference to authority that granted ownership rights."""


# =============================================================================
# GOAL AUTHORITY REFERENCE - Source of authority for the goal
# =============================================================================

@dataclass(frozen=True)
class GoalAuthorityReference:
    """
    Reference to the authority that governs this goal.
    
    Authority determines who can activate, suspend, modify, terminate, or
    abandon a goal. This is independent of ownership.
    """
    
    authority_id: str = "executive_authority"
    """Identifier for the governing authority."""
    
    authority_scope: Tuple[str, ...] = field(default_factory=tuple)
    """Scopes in which this authority applies (e.g., 'activation', 'modification')."""
    
    revision: int = 1
    """Authority definition revision number."""


# =============================================================================
# GOAL REFERENCE - Reference to an external goal
# =============================================================================

@dataclass(frozen=True)
class GoalReference:
    """
    Immutable reference to an externally owned goal.
    
    This is a reference only. The Executive Network does not own or contain
    the actual goal content. It holds metadata about how this goal relates
    to the current program.
    """
    
    goal_id: str = "exec_goal_ref_initial"
    """Unique identifier for the external goal."""
    
    revision: int = 1
    """Revision number of the external goal."""
    
    schema_version: str = "1.0.0"
    """Schema version of the external goal."""


# =============================================================================
# GOAL DEPENDENCY - Typed relationship between goals
# =============================================================================

class GoalDependencyKind(Enum):
    """
    Kinds of dependencies between goals.
    
    Dependencies describe ordering and constraint relationships,
    distinct from parent-child hierarchy.
    """
    
    REQUIRES = "requires"
    """This goal requires the target to be satisfied first."""
    
    BLOCKED_BY = "blocked_by"
    """This goal cannot proceed while target is active."""
    
    ENABLED_BY = "enabled_by"
    """Target enables this goal's strategy or approach."""
    
    PRECEDES = "precedes"
    """This goal must be completed before target begins."""
    
    FOLLOWS = "follows"
    """This goal follows target in the sequence."""
    
    MUTUALLY_EXCLUSIVE_WITH = "mutually_exclusive_with"
    """Both goals cannot be active simultaneously."""
    
    CONFLICTS_WITH = "conflicts_with"
    """Goals have conflicting requirements or outcomes."""
    
    SUPPORTS = "supports"
    """Target supports this goal's success."""
    
    WEAKENS = "weakens"
    """Target weakens this goal's prospects."""
    
    SUPERSEDES = "supersedes"
    """This goal replaces the target goal."""
    
    VERIFIES = "verifies"
    """Verification of target contributes to this goal."""
    
    RECOVERS = "recovers"
    """Recovery from target failure supports this goal."""
    
    MONITORS = "monitors"
    """Monitoring target contributes to this goal."""


@dataclass(frozen=True)
class GoalDependency:
    """
    Typed dependency relationship between two goals.
    
    Dependencies describe semantic ordering constraints, not parent-child
    decomposition relationships.
    """
    
    source_goal_reference: GoalReference
    """The goal that has the dependency."""
    
    target_goal_reference: GoalReference
    """The goal that is depended upon."""
    
    kind: GoalDependencyKind = GoalDependencyKind.REQUIRES
    """Type of dependency relationship."""
    
    condition: Optional[str] = None
    """Optional condition that must hold for this dependency."""
    
    strength: float = 1.0
    """Strength of the dependency (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in this dependency."""
    
    validity_seconds: Optional[float] = None
    """Time until this dependency is no longer valid."""
    
    provenance: str = "executive_network"
    """Source of this dependency knowledge."""


# =============================================================================
# GOAL SUPPORT RELATION - External support for a goal
# =============================================================================

@dataclass(frozen=True)
class GoalSupportRelation:
    """
    Evidence that another entity supports a goal.
    
    Support may come from:
        - Another goal (supporting goal structure)
        - A commitment (fulfillment requirement)
        - A plan (strategy alignment)
        - A capability (means to achieve)
        - A resource (necessary resources available)
        - Policy (authorization and guidance)
        - Security constraint (permission granted)
        - An action outcome (progress evidence)
    """
    
    source_reference_id: str = "exec_support_ref_initial"
    """Reference to the supporting entity."""
    
    support_kind: str = "general"
    """Kind of support (e.g., 'plan', 'capability', 'resource')."""
    
    strength: float = 1.0
    """Strength of support (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in the support assessment."""
    
    provenance: str = "executive_network"
    """Source of this support knowledge."""


# =============================================================================
# GOAL OBSTRUCTION RELATION - External obstruction to a goal
# =============================================================================

@dataclass(frozen=True)
class GoalObstructionRelation:
    """
    Evidence that another entity obstructs a goal.
    
    Obstruction may come from:
        - Another goal (competing objective)
        - A commitment (conflicting obligation)
        - A constraint (prohibitive rule)
        - A security prohibition (permission denied)
        - An action outcome (setback evidence)
    """
    
    source_reference_id: str = "exec_obstruct_ref_initial"
    """Reference to the obstructing entity."""
    
    obstruction_kind: str = "general"
    """Kind of obstruction (e.g., 'constraint', 'prohibition')."""
    
    severity: float = 1.0
    """Severity of obstruction (0.0 to 1.0)."""
    
    confidence: float = 1.0
    """Confidence in the obstruction assessment."""
    
    provenance: str = "executive_network"
    """Source of this obstruction knowledge."""


# =============================================================================
# GOAL SATISFACTION CRITERIA - Conditions for goal satisfaction
# =============================================================================

@dataclass(frozen=True)
class GoalSatisfactionCriteria:
    """
    Explicit criteria that must be satisfied for a goal to be considered
    successfully achieved.
    
    Satisfaction is determined by evidence, not proposal creation.
    """
    
    required_outcome_references: Tuple[str, ...] = field(default_factory=tuple)
    """Required outcomes or artifacts."""
    
    semantic_predicates: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic predicates that must hold."""
    
    artifact_existence_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions for artifact existence."""
    
    verification_result_reference: Optional[str] = None
    """Reference to required verification result."""
    
    accepted_authority_decision: bool = False
    """Whether authority acceptance is required."""
    
    maintained_state_duration_seconds: Optional[float] = None
    """Duration a state must be maintained."""
    
    child_goal_completion_required: Tuple[str, ...] = field(default_factory=tuple)
    """Child goals that must be completed."""
    
    fulfilled_commitment_references: Tuple[str, ...] = field(default_factory=tuple)
    """Commitments that must be fulfilled."""
    
    absence_of_prohibited_conditions: bool = False
    """Whether certain conditions must NOT hold."""
    
    confidence_threshold: float = 0.8
    """Minimum confidence required for satisfaction."""
    
    evidence_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Types of evidence that are acceptable."""


# =============================================================================
# GOAL SATISFACTION ASSESSMENT - Assessment of satisfaction status
# =============================================================================

class GoalSatisfactionAssessmentStatus(Enum):
    """
    Status of a goal satisfaction assessment.
    """
    
    NOT_ASSESSED = "not_assessed"
    """No assessment has been performed."""
    
    UNSATISFIED = "unsatisfied"
    """Criteria not met."""
    
    PARTIALLY_SATISFIED = "partially_satisfied"
    """Some criteria met but not complete."""
    
    SATISFIED = "satisfied"
    """All criteria satisfied."""
    
    DISPUTED = "disputed"
    """Satisfaction is contested."""
    
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    """Evidence insufficient for assessment."""
    
    INVALID_CRITERIA = "invalid_criteria"
    """Criteria are invalid or incoherent."""


@dataclass(frozen=True)
class GoalSatisfactionAssessment:
    """
    Assessment of whether a goal's satisfaction criteria have been met.
    
    The Executive Network may produce assessments from supplied evidence.
    It must not fabricate evidence.
    """
    
    status: GoalSatisfactionAssessmentStatus = GoalSatisfactionAssessmentStatus.NOT_ASSESSED
    """Current assessment status."""
    
    satisfied_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of criteria that have been met."""
    
    missing_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of criteria not yet met."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""
    
    assessment_confidence: float = 0.5
    """Confidence in this assessment (0.0 to 1.0)."""
    
    reason: str = ""
    """Explanation for the assessment."""
    
    provenance: str = "executive_network"
    """Source of this assessment."""


# =============================================================================
# GOAL FAILURE CRITERIA - Conditions for goal failure
# =============================================================================

@dataclass(frozen=True)
class GoalFailureCriteria:
    """
    Conditions under which a goal may be assessed as failed.
    
    Failure evidence does not automatically abandon a goal. Abandonment is
    a governance decision that may consider recovery options.
    """
    
    impossible_satisfaction: bool = False
    """Satisfaction is provably impossible."""
    
    invalidated_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions that invalidate the goal."""
    
    exhausted_strategies: bool = False
    """All admissible strategies have been exhausted."""
    
    permanent_dependency_failure: bool = False
    """Required dependencies have failed permanently."""
    
    policy_prohibition: bool = False
    """Policy now prohibits pursuit of this goal."""
    
    security_prohibition: bool = False
    """Security constraints prohibit pursuit."""
    
    expired_opportunity: bool = False
    """Time or opportunity window has closed."""
    
    external_rejection: bool = False
    """External authority has rejected the goal."""
    
    contradictory_objective: str = ""
    """Another objective directly contradicts this goal."""
    
    authority_revocation: bool = False
    """Authority has revoked permission to pursue."""


# =============================================================================
# GOAL FAILURE ASSESSMENT - Assessment of failure status
# =============================================================================

class GoalFailureAssessmentStatus(Enum):
    """
    Status of a goal failure assessment.
    """
    
    NO_FAILURE = "no_failure"
    """Goal is not failed."""
    
    RECOVERABLE_FAILURE = "recoverable_failure"
    """Failure may be recoverable with alternative strategy."""
    
    IRRECOVERABLE_FAILURE = "irrecoverable_failure"
    """Failure cannot be recovered; goal should be abandoned."""
    
    UNKNOWN = "unknown"
    """Cannot determine failure status from available evidence."""


@dataclass(frozen=True)
class GoalFailureAssessment:
    """
    Assessment of whether a goal has failed and the nature of that failure.
    
    Failure assessment informs but does not dictate abandonment decisions.
    """
    
    status: GoalFailureAssessmentStatus = GoalFailureAssessmentStatus.NO_FAILURE
    """Current failure status."""
    
    failure_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons identifying the failure."""
    
    evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting evidence."""
    
    recovery_possibility: float = 1.0
    """Probability that recovery is possible (0.0 to 1.0)."""
    
    alternative_strategies_available: bool = False
    """Whether alternative strategies remain viable."""
    
    confidence: float = 0.5
    """Confidence in this assessment."""
    
    provenance: str = "executive_network"
    """Source of this assessment."""


# =============================================================================
# GOAL ABANDONMENT CRITERIA - Conditions for abandonment consideration
# =============================================================================

@dataclass(frozen=True)
class GoalAbandonmentCriteria:
    """
    Conditions under which a goal may be considered for abandonment.
    
    Abandonment is always an executive/governance decision. It may consider
    failure assessment but also other factors like priority, cost, and
    opportunity.
    """
    
    failed_goal: bool = False
    """Goal has been assessed as failed."""
    
    permanently_unfeasible: bool = False
    """Goal is permanently infeasible."""
    
    lower_priority_alternative_exists: str = ""
    """Higher-priority alternative goal exists."""
    
    cost_benefit_negative: bool = False
    """Continued pursuit has negative net value."""
    
    opportunity_cost_high: bool = False
    """Opportunity cost of continuing is too high."""
    
    resource_reallocation_beneficial: bool = False
    """Resources would be better used elsewhere."""
    
    strategy_change_makes_irrelevant: bool = False
    """Strategy change makes this goal irrelevant."""


# =============================================================================
# GOAL ABANDONMENT PROPOSAL - Request to abandon a goal
# =============================================================================

@dataclass(frozen=True)
class GoalAbandonmentProposal:
    """
    Immutable proposal for goal abandonment.
    
    This is a request, not an action. No source goal is mutated directly.
    """
    
    goal_reference: GoalReference
    """Goal that would be abandoned."""
    
    reason: str = ""
    """Reason for proposing abandonment."""
    
    supporting_evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence supporting abandonment."""
    
    opposing_evidence_references: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence opposing abandonment."""
    
    authority_required: str = "executive_authority"
    """Authority that must approve this proposal."""
    
    confidence: float = 0.5
    """Confidence in the proposal assessment."""
    
    validity_seconds: Optional[float] = None
    """Time until proposal expires."""
    
    provenance: str = "executive_network"
    """Source of this proposal."""


# =============================================================================
# GOAL EXPIRATION - Time or event bound on a goal
# =============================================================================

@dataclass(frozen=True)
class GoalExpiration:
    """
    Expiration conditions for a goal.
    
    The Executive Network does not run timers. Expiration is evaluated from
    supplied SemanticTime or externally supplied events.
    """
    
    expiration_kind: str = "none"
    """Kind of expiration (time-bound, event-bound, etc.)."""
    
    time_bound_seconds: Optional[float] = None
    """Absolute time limit in seconds."""
    
    event_reference_id: Optional[str] = None
    """Reference to event that triggers expiration."""
    
    thread_bound_reference_id: Optional[str] = None
    """Thread whose termination causes expiration."""
    
    task_bound_reference_id: Optional[str] = None
    """Task whose completion causes expiration."""
    
    conversation_bound_reference_id: Optional[str] = None
    """Conversation whose end causes expiration."""
    
    authority_bound_reference_id: Optional[str] = None
    """Authority whose validity expires."""
    
    condition_reference_id: Optional[str] = None
    """Condition whose truth causes expiration."""
    
    opportunity_bound_reference_id: Optional[str] = None
    """Opportunity reference for time-limited opportunities."""


# =============================================================================
# EXECUTIVE GOAL PROJECTION - Complete goal projection with metadata
# =============================================================================

@dataclass(frozen=True)
class ExecutiveGoalProjection:
    """
    Immutable, complete projection of a goal into the Executive Network.
    
    This combines all metadata about how an externally owned goal relates to
    the current executive organization.
    
    The underlying goal remains externally owned. This is a bounded,
    immutable view for one assessment cycle.
    """
    
    # Identity and revisioning
    goal_id: str = "exec_goal_ref_initial"
    """Unique identifier for the external goal."""
    
    revision: int = 1
    """Revision number of the external goal."""
    
    schema_version: str = "1.0.0"
    """Schema version of the external goal."""
    
    # Semantic classification
    kind: GoalKind = GoalKind.GENERAL
    """Semantic category of the goal."""
    
    statement: str = ""
    """Natural language description of the goal."""
    
    desired_condition: Optional[str] = None
    """The desired condition or state."""
    
    avoidance_condition: Optional[str] = None
    """Condition to be avoided, if any."""
    
    # Ownership and authority (preserved from source)
    owner_reference: GoalOwnerReference = field(
        default_factory=GoalOwnerReference
    )
    """Reference to the goal's owner."""
    
    authority_reference: GoalAuthorityReference = field(
        default_factory=GoalAuthorityReference
    )
    """Reference to the governing authority."""
    
    # Lifecycle status
    status: GoalStatus = GoalStatus.PROPOSED
    """Current semantic lifecycle status."""
    
    activation_state: GoalActivationState = GoalActivationState.INACTIVE
    """Executive Network's view of activation state."""
    
    origin: str = "external"
    """Origin of this goal (e.g., 'user', 'system', 'policy')."""
    
    # Hierarchy and relationships
    parent_goal_reference: Optional[GoalReference] = None
    """Parent goal in hierarchy, if any."""
    
    child_goal_references: Tuple[GoalReference, ...] = field(
        default_factory=tuple
    )
    """Child goals in hierarchy."""
    
    dependencies: Tuple[GoalDependency, ...] = field(default_factory=tuple)
    """Dependencies on other goals."""
    
    supported_by: Tuple[GoalSupportRelation, ...] = field(default_factory=tuple)
    """Entities that support this goal."""
    
    obstructed_by: Tuple[GoalObstructionRelation, ...] = field(
        default_factory=tuple
    )
    """Entities that obstruct this goal."""
    
    # Satisfaction criteria and assessment
    satisfaction_criteria: GoalSatisfactionCriteria = field(
        default_factory=GoalSatisfactionCriteria
    )
    """Conditions for satisfaction."""
    
    failure_criteria: GoalFailureCriteria = field(
        default_factory=GoalFailureCriteria
    )
    """Conditions for failure."""
    
    abandonment_criteria: GoalAbandonmentCriteria = field(
        default_factory=GoalAbandonmentCriteria
    )
    """Conditions under which abandonment may be considered."""
    
    expiration: Optional[GoalExpiration] = None
    """Expiration conditions, if any."""
    
    # Temporal and confidence metrics
    temporal_profile: str = "ongoing"
    """Temporal characteristics (e.g., 'time-bound', 'ongoing')."""
    
    confidence: float = 0.5
    """Confidence in goal formation and criteria."""
    
    completeness: float = 0.5
    """Completeness of the projection."""
    
    factuality: str = "provisional"
    """Factuality classification (e.g., 'verified', 'provisional')."""
    
    privacy: str = "internal"
    """Privacy classification."""
    
    provenance: str = "executive_network"
    """Source of this projection."""


# =============================================================================
# EXECUTIVE GOAL BINDING - Goal bound to an ExecutiveProgram
# =============================================================================

@dataclass(frozen=True)
class ExecutiveGoalBinding:
    """
    Binding that associates a goal with an ExecutiveProgram, along with all
    executive metadata.
    
    A binding is owned by the Executive Network. The underlying goal may be
    externally owned. This is the canonical contract for Phase 4.4.4.
    """
    
    # Identity and revisioning
    binding_id: str = "exec_goal_binding_initial"
    """Unique identifier for this binding."""
    
    binding_revision: int = 1
    """Revision number of this binding."""
    
    schema_version: str = "1.0.0"
    """Schema version of the binding contract."""
    
    # Goal reference (external ownership preserved)
    goal_reference: GoalReference = field(default_factory=GoalReference)
    """Reference to the external goal."""
    
    program_reference_id: str = "exec_program_initial"
    """ID of the ExecutiveProgram that owns this binding."""
    
    task_set_reference_id: str = "exec_taskset_initial"
    """ID of the ExecutiveTaskSet containing this binding."""
    
    # Binding role
    binding_role: str = "primary"
    """Role in the program (e.g., 'primary', 'supporting', 'subgoal')."""
    
    # Activation state (Executive Network's view)
    activation_state: GoalActivationState = GoalActivationState.INACTIVE
    """Current activation state."""
    
    # Authority (for lifecycle decisions)
    authority_reference: GoalAuthorityReference = field(
        default_factory=GoalAuthorityReference
    )
    """Authority that can modify this binding."""
    
    # Executive metrics
    executive_relevance: float = 0.5
    """Relevance to current program objectives."""
    
    executive_priority_assessment: int = 50
    """Executive priority assessment (relative ordering)."""
    
    # Dependencies and requirements
    dependency_references: Tuple[str, ...] = field(default_factory=tuple)
    """References to dependencies."""
    
    satisfaction_criteria_reference: Optional[str] = None
    """Reference to satisfaction criteria definition."""
    
    control_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Control requirements for this goal."""
    
    focus_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Attentional focus requirements."""
    
    working_memory_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Working Memory state requirements."""
    
    monitoring_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Monitoring requirements."""
    
    # Temporal validity
    temporal_validity_seconds: Optional[float] = None
    """Time until this binding expires."""
    
    # Quality metrics
    confidence: float = 0.5
    """Confidence in the binding assessment."""
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Known limitations of this binding."""
    
    privacy: str = "internal"
    """Privacy classification."""
    
    provenance: str = "executive_network"
    """Source of this binding."""


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    # Kinds and states
    "GoalKind",
    "GoalStatus",
    "GoalActivationState",
    
    # References
    "GoalOwnerReference",
    "GoalAuthorityReference",
    "GoalReference",
    
    # Dependencies and relations
    "GoalDependencyKind",
    "GoalDependency",
    "GoalSupportRelation",
    "GoalObstructionRelation",
    
    # Satisfaction
    "GoalSatisfactionCriteria",
    "GoalSatisfactionAssessmentStatus",
    "GoalSatisfactionAssessment",
    
    # Failure
    "GoalFailureCriteria",
    "GoalFailureAssessmentStatus",
    "GoalFailureAssessment",
    
    # Abandonment
    "GoalAbandonmentCriteria",
    "GoalAbandonmentProposal",
    
    # Expiration
    "GoalExpiration",
    
    # Projections and bindings (Phase 4.4.4 canonical)
    "ExecutiveGoalProjection",
    "ExecutiveGoalBinding",
)