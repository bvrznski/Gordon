# Executive Goals Package
# ======================

"""
Executive Goals - Canonical semantic architecture for goal projections,
bindings, hierarchies, dependencies, lifecycles, and coordination.

This is Phase 4.4.4: Goal, Commitment, and Priority Coordination.

ARCHITECTURAL PRINCIPLES
========================

EXEC-GOAL-001: Goals describe desired conditions
    A goal is a semantic representation of a desired state, outcome,
    or condition. It is not a task, plan, or commitment.

EXEC-GOAL-002: Goal projections are immutable
    All goal projections are frozen dataclasses. No mutable references.

EXEC-GOAL-003: Bindings reference external goals
    Executive goal bindings hold references to externally owned goals.
    They do NOT copy goal content.

EXEC-GOAL-004: Authority is explicit and preserved
    Every goal projection preserves its source owner, authority,
    revision, factuality, privacy, and provenance.

EXEC-GOAL-005: Goals are distinct from tasks
    A goal describes a desired condition. A task describes work to
    achieve that condition. They remain semantically separate.

EXEC-GOAL-006: Goals are distinct from plans
    A goal is WHAT is desired. A plan is HOW it might be achieved.
    Plans are owned by Planning, goals are owned by the Executive.

EXEC-GOAL-007: Hierarchy and dependency are distinct
    Parent-child hierarchy describes decomposition.
    Dependencies describe ordering constraints.
    They may overlap but remain conceptually separate.

EXEC-GOAL-008: Cycles in hierarchy are rejected
    Goal hierarchy forms a directed acyclic graph (DAG).
    Any cycle detection results in rejection.

EXEC-GOAL-009: Satisfaction requires evidence
    Goal satisfaction is determined by explicit criteria and
    verifiable evidence. It is not inferred from proposal creation.

EXEC-GOAL-010: Failure does not imply abandonment
    A goal may fail but remain active pending alternative strategy review.
    Abandonment is a governance decision.

EXEC-GOAL-011: Expiration is explicit
    Goals may have time-bound, event-bound, or condition-bound expiration.
    The Executive Network does not run timers; evaluation is external.

EXEC-GOAL-012: Lifecycle proposals are immutable
    All lifecycle change requests (activation, suspension, termination,
    completion, failure, abandonment) produce immutable proposal objects.
    No source goal is mutated directly.

EXEC-GOAL-013: Priority assessment remains decomposable
    Executive priority assessments break down into evidence dimensions:
    urgency, importance, relevance, feasibility, persistence, and pressure.
    They are NOT reduced to a single opaque score.

EXEC-GOAL-014: Binding does not transfer ownership
    When a goal is bound to an ExecutiveProgram, the source owner
    remains unchanged. Only the binding metadata is owned by the Executive.

EXEC-GOAL-015: Deterministic ordering is required
    Given identical inputs (state, context, program, config), the same
    priority orderings and assessments are always produced.

EXEC-GOAL-016: Bounded comparison prevents O(n²) explosion
    Pairwise comparison of goals/commitments has explicit capacity limits.
    Large sets require prefiltering or top-k selection.

EXEC-GOAL-017: Incomparability is supported
    Not all items can be meaningfully compared. Partial ordering
    supports explicitly labeled incomparable pairs.

EXEC-GOAL-018: Tie handling must be deterministic
    When priorities are equal, deterministic tie-breaking rules apply.
    No random choice, hash order, or insertion order unless explicitly declared.

EXEC-GOAL-019: Policy and security constraints are not ordinary preferences
    Mandatory policy requirements and security prohibitions cannot be
    outweighed by priority scores. They remain categorical constraints.

EXEC-GOAL-020: Motivational and attentional evidence is external
    Motivation and Attention Networks provide projections as advisory.
    The Executive may consume them but does not create or own them.

EXEC-GOAL-021: Serialization preserves all semantic information
    Round-trip serialization must preserve type discriminators,
    schema versions, IDs, revisions, status, activation, owner, authority,
    hierarchy, dependencies, relations, criteria, priority dimensions,
    conflicts, privacy, factuality, confidence, provenance.

EXEC-GOAL-022: Validation occurs at all boundaries
    Every public API validates input for structural correctness,
    authority compliance, revision consistency, factuality, and boundedness.

EXEC-GOAL-023: State integration uses deltas and transitions
    ExecutiveState is never mutated directly. All changes use
    ExecutiveStateDelta through the canonical transition mechanism.

EXEC-GOAL-024: Import safety is preserved
    Package import performs no goal activation, priority computation,
    authority decision, or subsystem access.

VERSION: 1.0.0
COMPATIBILITY: forward (phased implementation)
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

from __future__ import annotations

# =============================================================================
# CORE PROJECTION TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.goals.projection import (
    ExecutiveGoalProjection,
    ExecutiveGoalBinding,
)

from gordon_system.src.agent.networks.executive.goals.kind import GoalKind
from gordon_system.src.agent.networks.executive.goals.status import GoalStatus
from gordon_system.src.agent.networks.executive.goals.activation import (
    GoalActivationState,
)

# =============================================================================
# HIERARCHY AND DEPENDENCY TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.goals.dependency import (
    GoalDependency,
    GoalDependencyKind,
)

from gordon_system.src.agent.networks.executive.goals.relation import (
    GoalSupportRelation,
    GoalObstructionRelation,
)

# =============================================================================
# SATISFACTION AND FAILURE TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.goals.satisfaction import (
    GoalSatisfactionCriteria,
    GoalSatisfactionAssessment,
)

from gordon_system.src.agent.networks.executive.goals.failure import (
    GoalFailureCriteria,
    GoalFailureAssessment,
    GoalAbandonmentCriteria,
    GoalAbandonmentProposal,
)

# =============================================================================
# EXPIRATION TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.goals.expiration import (
    GoalExpiration,
)

# =============================================================================
# LIFECYCLE PROPOSAL TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.goals.proposal import (
    GoalActivationProposal,
    GoalSuspensionProposal,
    GoalReactivationProposal,
    GoalCompletionProposal,
    GoalFailureProposal,
    GoalAbandonmentProposal,
    GoalTerminationProposal,
    GoalSupersessionProposal,
    GoalRevisionProposal,
)

# =============================================================================
# PRIORITY ASSESSMENT TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.priorities.assessment import (
    ExecutivePriorityAssessment,
)

from gordon_system.src.agent.networks.executive.priorities.level import (
    ExecutivePriorityLevel,
)

from gordon_system.src.agent.networks.executive.priorities.ordering import (
    ExecutivePriorityOrdering,
    ExecutivePriorityRelation,
)

# =============================================================================
# PRIORITY DIMENSION TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.priorities.urgency import (
    ExecutiveUrgencyAssessment,
)

from gordon_system.src.agent.networks.executive.priorities.importance import (
    ExecutiveImportanceAssessment,
)

# Priority dimension imports are commented - modules to be created
# from gordon_system.src.agent.networks.executive.priorities.relevance import (
#     ExecutiveRelevanceAssessment,
# )
# from gordon_system.src.agent.networks.executive.priorities.feasibility import (
#     ExecutiveFeasibilityAssessment,
# )


from gordon_system.src.agent.networks.executive.priorities.persistence import (
    ExecutivePersistenceAssessment,
)

# =============================================================================
# PRESSURE TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.priorities.pressure import (
    CommitmentPressureAssessment,
    RiskPressureAssessment,
    OpportunityPressureAssessment,
    DependencyPressureAssessment,
    PolicyPressureAssessment,
    SecurityPressureAssessment,
)

# =============================================================================
# CONFLICT TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.priorities.conflict import (
    PriorityConflict,
    PriorityConflictKind,
)

# =============================================================================
# PRIORITY RECOMMENDATION AND PROPOSAL TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.priorities.recommendation import (
    ExecutivePriorityRecommendation,
)

from gordon_system.src.agent.networks.executive.priorities.proposal import (
    ExecutivePriorityRevisionProposal,
)

# =============================================================================
# ALGORITHM TYPES (no implementation - just types)
# =============================================================================

from gordon_system.src.agent.networks.executive.algorithms import (
    ExecutiveProgramGoalAlignment,
    ExecutiveProgramCommitmentAlignment,
    TaskSetGoalAlignment,
    TaskSetCommitmentAlignment,
)

# =============================================================================
# COORDINATION REQUEST AND OUTCOME TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.coordination.request import (
    GoalCommitmentCoordinationRequest,
)

from gordon_system.src.agent.networks.executive.coordination.scope import (
    GoalCommitmentCoordinationScope,
)

from gordon_system.src.agent.networks.executive.coordination.plan import (
    GoalCommitmentCoordinationPlan,
)

from gordon_system.src.agent.networks.executive.coordination.products import (
    GoalCommitmentCoordinationProduct,
)

from gordon_system.src.agent.networks.executive.coordination.outcome import (
    GoalCommitmentCoordinationOutcome,
)

from gordon_system.src.agent.networks.executive.coordination.continuation import (
    GoalCommitmentCoordinationContinuation,
)

from gordon_system.src.agent.networks.executive.coordination.state import (
    GoalCommitmentCoordinationState,
)

# =============================================================================
# GOAL-COMMITMENT RELATION TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.goals.commitment_relation import (
    GoalCommitmentRelation,
    GoalCommitmentRelationKind,
)

# =============================================================================
# COMMITMENT PROJECTION AND BINDING TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.commitments.projection import (
    ExecutiveCommitmentProjection,
    ExecutiveCommitmentBinding,
)

from gordon_system.src.agent.networks.executive.commitments.kind import CommitmentKind
from gordon_system.src.agent.networks.executive.commitments.status import (
    CommitmentStatus,
)
from gordon_system.src.agent.networks.executive.commitments.activation import (
    CommitmentActivationState,
)

# =============================================================================
# COMMITMENT LIFECYCLE TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.commitments.fulfillment import (
    CommitmentFulfillmentCriteria,
    CommitmentFulfillmentAssessment,
)

from gordon_system.src.agent.networks.executive.commitments.breach import (
    CommitmentBreachCriteria,
    CommitmentBreachAssessment,
)

from gordon_system.src.agent.networks.executive.commitments.release import (
    CommitmentReleaseConditions,
    CommitmentReleaseProposal,
    CommitmentReleaseDecisionReference,
)

# =============================================================================
# COMMITMENT EXPIRATION
# =============================================================================

from gordon_system.src.agent.networks.executive.commitments.expiration import (
    CommitmentExpiration,
)

# =============================================================================
# COMMITMENT LIFECYCLE PROPOSAL TYPES
# =============================================================================

from gordon_system.src.agent.networks.executive.commitments.proposal import (
    CommitmentActivationProposal,
    CommitmentSuspensionProposal,
    CommitmentFulfillmentProposal,
    CommitmentBreachReviewProposal,
    CommitmentReleaseProposal,
    CommitmentTerminationProposal,
    CommitmentRevisionProposal,
    CommitmentEscalationProposal,
)

# =============================================================================
# EXPORTS - Canonical public API
# =============================================================================

__all__: tuple[str, ...] = (
    # Goal projections and bindings (Phase 4.4.4)
    "ExecutiveGoalProjection",
    "ExecutiveGoalBinding",
    
    # Goal kinds and states
    "GoalKind",
    "GoalStatus",
    "GoalActivationState",
    
    # Goal hierarchy and dependencies
    "GoalDependency",
    "GoalDependencyKind",
    "GoalSupportRelation",
    "GoalObstructionRelation",
    
    # Goal satisfaction and failure
    "GoalSatisfactionCriteria",
    "GoalSatisfactionAssessment",
    "GoalFailureCriteria",
    "GoalFailureAssessment",
    "GoalAbandonmentCriteria",
    "GoalAbandonmentProposal",
    
    # Goal expiration
    "GoalExpiration",
    
    # Goal lifecycle proposals
    "GoalActivationProposal",
    "GoalSuspensionProposal",
    "GoalReactivationProposal",
    "GoalCompletionProposal",
    "GoalFailureProposal",
    "GoalAbandonmentProposal",
    "GoalTerminationProposal",
    "GoalSupersessionProposal",
    "GoalRevisionProposal",
    
    # Priority assessment
    "ExecutivePriorityAssessment",
    "ExecutivePriorityLevel",
    "ExecutivePriorityOrdering",
    "ExecutivePriorityRelation",
    
    # Priority dimensions
    "ExecutiveUrgencyAssessment",
    "ExecutiveImportanceAssessment",
    "ExecutiveRelevanceAssessment",
    "ExecutiveFeasibilityAssessment",
    "ExecutivePersistenceAssessment",
    
    # Pressure assessments
    "CommitmentPressureAssessment",
    "RiskPressureAssessment",
    "OpportunityPressureAssessment",
    "DependencyPressureAssessment",
    "PolicyPressureAssessment",
    "SecurityPressureAssessment",
    
    # Priority conflicts and recommendations
    "PriorityConflict",
    "PriorityConflictKind",
    "ExecutivePriorityRecommendation",
    "ExecutivePriorityRevisionProposal",
    
    # Program alignment
    "ExecutiveProgramGoalAlignment",
    "ExecutiveProgramCommitmentAlignment",
    "TaskSetGoalAlignment",
    "TaskSetCommitmentAlignment",
    
    # Coordination
    "GoalCommitmentCoordinationRequest",
    "GoalCommitmentCoordinationScope",
    "GoalCommitmentCoordinationPlan",
    "GoalCommitmentCoordinationProduct",
    "GoalCommitmentCoordinationOutcome",
    "GoalCommitmentCoordinationContinuation",
    "GoalCommitmentCoordinationState",
    
    # Goal-commitment relations
    "GoalCommitmentRelation",
    "GoalCommitmentRelationKind",
    
    # Commitment projections and bindings
    "ExecutiveCommitmentProjection",
    "ExecutiveCommitmentBinding",
    
    # Commitment kinds and states
    "CommitmentKind",
    "CommitmentStatus",
    "CommitmentActivationState",
    
    # Commitment lifecycle
    "CommitmentFulfillmentCriteria",
    "CommitmentFulfillmentAssessment",
    "CommitmentBreachCriteria",
    "CommitmentBreachAssessment",
    "CommitmentReleaseConditions",
    "CommitmentReleaseProposal",
    "CommitmentReleaseDecisionReference",
    "CommitmentExpiration",
    
    # Commitment lifecycle proposals
    "CommitmentActivationProposal",
    "CommitmentSuspensionProposal",
    "CommitmentFulfillmentProposal",
    "CommitmentBreachReviewProposal",
    "CommitmentReleaseProposal",
    "CommitmentTerminationProposal",
    "CommitmentRevisionProposal",
    "CommitmentEscalationProposal",
)