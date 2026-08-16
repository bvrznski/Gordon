# Executive Strategy Model
# =========================

"""
Canonical ExecutiveStrategy immutable dataclass.

This module defines:
- ExecutiveStrategyId: Unique identifier for strategies
- ExecutiveStrategyRevision: Monotonic revision tracker
- ExecutiveStrategySubject: The subject being addressed
- ExecutiveStrategyScope: Bounded scope of application
- ExecutiveStrategy: The core strategy definition
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# EXECUTIVE STRATEGY ID - UNIQUE IDENTIFIER
# =============================================================================

@dataclass(frozen=True)
class ExecutiveStrategyId:
    """Unique identifier for an executive strategy."""
    value: str = "exec_strategy_default"
    
    @classmethod
    def new(cls, value: str) -> "ExecutiveStrategyId":
        return cls(value=value)


# =============================================================================
# EXECUTIVE STRATEGY REVISION - VERSION TRACKING
# =============================================================================

@dataclass(frozen=True)
class ExecutiveStrategyRevision:
    """Monotonic revision number for strategy versioning."""
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    @classmethod
    def initial(cls) -> "ExecutiveStrategyRevision":
        return cls(major=1, minor=0, patch=0)
    
    def bump_major(self) -> "ExecutiveStrategyRevision":
        return cls(major=self.major + 1, minor=0, patch=0)
    
    def bump_minor(self) -> "ExecutiveStrategyRevision":
        return cls(major=self.major, minor=self.minor + 1, patch=0)
    
    def bump_patch(self) -> "ExecutiveStrategyRevision":
        return cls(major=self.major, minor=self.minor, patch=self.patch + 1)


# =============================================================================
# EXECUTIVE STRATEGY SUBJECT - WHAT THE STRATEGY ADDRESSES
# =============================================================================

class ExecutiveStrategySubjectKind(Enum):
    """Kinds of strategy subjects."""
    EXECUTIVE_PROGRAM = "executive_program"
    EXECUTIVE_TASK_SET = "executive_task_set"
    GOAL = "goal"
    GOAL_SET = "goal_set"
    COMMITMENT = "commitment"
    COMMITMENT_SET = "commitment_set"
    TASK = "task"
    CONVERSATION = "conversation"
    DECISION = "decision"
    RECOVERY = "recovery"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"
    GENERAL_EXECUTIVE_UNDERTAKING = "general_executive_undertaking"


@dataclass(frozen=True)
class ExecutiveStrategySubject:
    """The subject a strategy addresses."""
    kind: ExecutiveStrategySubjectKind
    reference_id: str = ""
    
    @classmethod
    def for_program(cls, program_id: str) -> "ExecutiveStrategySubject":
        return cls(
            kind=ExecutiveStrategySubjectKind.EXECUTIVE_PROGRAM,
            reference_id=program_id
        )
    
    @classmethod
    def for_task_set(cls, task_set_id: str) -> "ExecutiveStrategySubject":
        return cls(
            kind=ExecutiveStrategySubjectKind.EXECUTIVE_TASK_SET,
            reference_id=task_set_id
        )
    
    @classmethod
    def for_goal(cls, goal_id: str) -> "ExecutiveStrategySubject":
        return cls(
            kind=ExecutiveStrategySubjectKind.GOAL,
            reference_id=goal_id
        )


# =============================================================================
# EXECUTIVE STRATEGY SCOPE - BOUNDED APPLICATION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveStrategyScope:
    """Bounded scope of strategy application."""
    program_scope: bool = False
    task_set_scope: bool = False
    thread_scope: bool = False
    task_scope: bool = False
    conversation_scope: bool = False
    participant_scope: bool = False
    goal_scope: bool = False
    commitment_scope: bool = False
    decision_scope: bool = False
    temporal_scope_seconds: Optional[float] = None
    authority_scope: bool = False
    policy_scope: bool = False
    security_scope: bool = False
    privacy_scope: bool = False
    
    @classmethod
    def local(cls) -> "ExecutiveStrategyScope":
        """Create a local (bounded) scope."""
        return cls(
            program_scope=True,
            task_set_scope=True,
            thread_scope=True,
            temporal_scope_seconds=3600.0,  # 1 hour default
        )
    
    @classmethod
    def global_(cls) -> "ExecutiveStrategyScope":
        """Create a global scope (should be used sparingly)."""
        return cls(
            program_scope=True,
            task_set_scope=True,
            thread_scope=True,
            conversation_scope=True,
            participant_scope=True,
            temporal_scope_seconds=None,  # No time limit
        )


# =============================================================================
# EXECUTIVE STRATEGY PURPOSE - WHAT IT AIMS TO ACHIEVE
# =============================================================================

class ExecutiveStrategyPurpose(Enum):
    """Purposes a strategy can serve."""
    ACHIEVE_GOAL = "achieve_goal"
    FULFILL_COMMITMENT = "fulfill_commitment"
    COMPLETE_PROGRAM = "complete_program"
    REDUCE_UNCERTAINTY = "reduce_uncertainty"
    RESOLVE_CONFLICT = "resolve_conflict"
    RECOVER_PROGRESS = "recover_progress"
    MAINTAIN_STABILITY = "maintain_stability"
    IMPROVE_PERFORMANCE = "improve_performance"
    REDUCE_ERROR = "reduce_error"
    PREPARE_DECISION = "prepare_decision"
    PREPARE_ACTION_SELECTION = "prepare_action_selection"
    COORDINATE_COMMUNICATION = "coordinate_communication"
    PRESERVE_POLICY_COMPLIANCE = "preserve_policy_compliance"
    PRESERVE_SECURITY_COMPLIANCE = "preserve_security_compliance"
    MANAGE_OVERLOAD = "manage_overload"
    SUPPORT_MONITORING = "support_monitoring"
    SUPPORT_RECOVERY = "support_recovery"
    GENERAL_EXECUTIVE_PURSUIT = "general_executive_pursuit"


# =============================================================================
# EXECUTIVE STRATEGY KIND - TYPE OF STRATEGY
# =============================================================================

class ExecutiveStrategyKind(Enum):
    """Kinds of strategies."""
    DIRECT = "direct"
    INCREMENTAL = "incremental"
    ITERATIVE = "iterative"
    HIERARCHICAL = "hierarchical"
    DECOMPOSITION_BASED = "decomposition_based"
    EVIDENCE_FIRST = "evidence_first"
    CONSTRAINT_FIRST = "constraint_first"
    RISK_MINIMIZING = "risk_minimizing"
    OPPORTUNITY_SEEKING = "opportunity_seeking"
    REVERSIBILITY_PRESERVING = "reversibility_preserving"
    RECOVERY_ORIENTED = "recovery_oriented"
    MONITORING_ORIENTED = "monitoring_oriented"
    EXPLORATORY = "exploratory"
    EXPLOITATIVE = "exploitative"
    VERIFICATION_ORIENTED = "verification_oriented"
    COMMUNICATION_ORIENTED = "communication_oriented"
    USER_GUIDED = "user_guided"
    POLICY_CONSTRAINED = "policy_constrained"
    SECURITY_CONSTRAINED = "security_constrained"
    COLLABORATIVE = "collaborative"
    DELEGATED = "delegated"
    FALLBACK = "fallback"
    MAINTENANCE = "maintenance"
    GENERAL = "general"
    UNKNOWN = "unknown"


# =============================================================================
# EXECUTIVE STRATEGY STATUS - LIFECYCLE STATUS
# =============================================================================

class ExecutiveStrategyStatus(Enum):
    """Status of a strategy in its lifecycle."""
    PROPOSED = "proposed"
    UNDER_REVIEW = "under_review"
    ELIGIBLE = "eligible"
    READY = "ready"
    ACTIVE = "active"
    MAINTAINED = "maintained"
    PARTIALLY_ACTIVE = "partially_active"
    SUSPENDED = "suspended"
    WAITING = "waiting"
    UNDER_REVISION = "under_revision"
    REPLACEMENT_PROPOSED = "replacement_proposed"
    RESTORATION_PROPOSED = "restoration_proposed"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    INEFFECTIVE = "ineffective"
    COUNTERPRODUCTIVE = "counterproductive"
    ABANDONED = "abandoned"
    TERMINATED = "terminated"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"
    EXPIRED = "expired"
    INVALID = "invalid"
    UNKNOWN = "unknown"


# =============================================================================
# EXECUTIVE STRATEGY ACTIVATION STATE - CURRENT STATE
# =============================================================================

class ExecutiveStrategyActivationState(Enum):
    """Current activation state of a strategy."""
    INACTIVE = "inactive"
    CANDIDATE = "candidate"
    PROPOSED_FOR_ACTIVATION = "proposed_for_activation"
    ACTIVE = "active"
    PROPOSED_FOR_MAINTENANCE = "proposed_for_maintenance"
    PROPOSED_FOR_SUSPENSION = "proposed_for_suspension"
    SUSPENDED = "suspended"
    PROPOSED_FOR_RESTORATION = "proposed_for_restoration"
    PROPOSED_FOR_REPLACEMENT = "proposed_for_replacement"
    TERMINAL = "terminal"
    UNKNOWN = "unknown"


# =============================================================================
# EXECUTIVE STRATEGY - THE CORE DEFINITION
# =============================================================================

@dataclass(frozen=True)
class ExecutiveStrategy:
    """
    Canonical immutable representation of an executive strategy.
    
    A Strategy describes the general approach through which an undertaking
    should be organized. It is NOT executable code, a plan, or a list of actions.
    
    Properties:
        - Immutable: No in-place modification; create new instances for changes
        - Bounded: All collections have capacity limits
        - Revisioned: Each strategy has an increasing revision number
        - Deterministic: Same inputs produce same outputs
        - Serializable: Can be converted to/from dict for storage
    """
    
    # Identity and revisioning
    strategy_id: ExecutiveStrategyId
    """Unique identifier for this strategy instance."""
    
    revision: ExecutiveStrategyRevision = field(default_factory=ExecutiveStrategyRevision.initial)
    """Current revision number with schema version tracking."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Subject and scope
    subject: ExecutiveStrategySubject
    """The subject this strategy addresses."""
    
    scope: ExecutiveStrategyScope = field(default_factory=ExecutiveStrategyScope.local)
    """Bounded scope of application."""
    
    # Purpose and kind
    purpose: ExecutiveStrategyPurpose = ExecutiveStrategyPurpose.GENERAL_EXECUTIVE_PURSUIT
    """Purpose/goal of the strategy."""
    
    kind: ExecutiveStrategyKind = ExecutiveStrategyKind.GENERAL
    """Type/classification of strategy."""
    
    status: ExecutiveStrategyStatus = ExecutiveStrategyStatus.PROPOSED
    """Lifecycle status."""
    
    activation_state: ExecutiveStrategyActivationState = ExecutiveStrategyActivationState.INACTIVE
    """Current activation state."""
    
    # Authority and ownership (references only, not full objects)
    owner_reference_id: Optional[str] = None
    """ID of strategy owner (external system reference)."""
    
    authority_id: Optional[str] = None
    """ID of authority that governs this strategy."""
    
    # Program references (not full programs - just references)
    program_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of programs this strategy supports."""
    
    task_set_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of task sets this strategy applies to."""
    
    goal_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of goals supported by this strategy."""
    
    commitment_reference_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of commitments addressed by this strategy."""
    
    # Strategy content (principles, assumptions, etc.)
    principles: Tuple[str, ...] = field(default_factory=tuple)
    """Guiding principles."""
    
    assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Critical assumptions."""
    
    preconditions: Tuple[str, ...] = field(default_factory=tuple)
    """Required preconditions."""
    
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    """Applicable constraints."""
    
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """Strategy dependencies."""
    
    # Evidence and monitoring requirements
    evidence_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Required evidence for activation."""
    
    monitoring_requirements: Tuple[str, ...] = field(default_factory=tuple)
    """Monitoring requirements."""
    
    performance_criteria_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of performance criteria."""
    
    completion_criteria_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of completion criteria."""
    
    failure_criteria_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of failure criteria."""
    
    abandonment_criteria_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of abandonment criteria."""
    
    # Fallback and recovery
    fallback_reference_id: Optional[str] = None
    """ID of fallback strategy (if any)."""
    
    recovery_conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Recovery conditions."""
    
    alternatives: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of alternative strategies."""
    
    # Evaluations
    applicability_status: str = "unknown"
    """Applicability assessment status."""
    
    feasibility_score: float = 0.5
    """Feasibility score (0.0-1.0)."""
    
    adequacy_score: float = 0.5
    """Adequacy score (0.0-1.0)."""
    
    risk_assessment: str = "unknown"
    """Risk assessment classification."""
    
    cost_assessment: str = "unknown"
    """Cost assessment classification."""
    
    benefit_assessment: str = "unknown"
    """Benefit assessment classification."""
    
    reversibility_status: str = "unknown"
    """Reversibility classification."""
    
    adaptability_status: str = "unknown"
    """Adaptability classification."""
    
    persistence_kind: str = "program_scoped"
    """Persistence characteristics."""
    
    # Quality metrics
    confidence_score: float = 0.5
    """Confidence in the strategy."""
    
    completeness_score: float = 0.5
    """Completeness score."""
    
    consistency_score: float = 1.0
    """Consistency score."""
    
    coherence_score: float = 1.0
    """Coherence score."""
    
    validity_status: str = "unknown"
    """Validity classification."""
    
    # Metadata
    privacy_classification: str = "internal"
    """Privacy classification."""
    
    provenance_created_by: str = "executive_network"
    """Who/what created this strategy."""
    
    provenance_created_at_utc: float = 0.0
    """When created (seconds since epoch)."""
    
    # Capacity limits
    max_principles: int = 50
    """Maximum principles allowed."""
    max_assumptions: int = 100
    """Maximum assumptions allowed."""
    max_preconditions: int = 100
    """Maximum preconditions allowed."""
    max_constraints: int = 200
    """Maximum constraints allowed."""
    
    @classmethod
    def initial(
        cls,
        strategy_id: str = "exec_strategy_initial",
        subject_kind: ExecutiveStrategySubjectKind = ExecutiveStrategySubjectKind.EXECUTIVE_PROGRAM,
        subject_reference_id: str = "exec_program_initial",
    ) -> "ExecutiveStrategy":
        """
        Create an initial executive strategy.
        
        Args:
            strategy_id: Unique identifier for the new strategy
            subject_kind: Kind of subject this strategy addresses
            subject_reference_id: Reference ID of the subject
            
        Returns:
            New strategy in PROPOSED/INACTIVE state with initial revision
        """
        return cls(
            strategy_id=ExecutiveStrategyId.new(strategy_id),
            subject=ExecutiveStrategySubject(kind=subject_kind, reference_id=subject_reference_id),
            scope=ExecutiveStrategyScope.local(),
            purpose=ExecutiveStrategyPurpose.GENERAL_EXECUTIVE_PURSUIT,
            kind=ExecutiveStrategyKind.GENERAL,
        )
    
    @property
    def is_terminal(self) -> bool:
        """Check if strategy has reached a terminal status."""
        return self.status in (
            ExecutiveStrategyStatus.COMPLETED,
            ExecutiveStrategyStatus.FAILED,
            ExecutiveStrategyStatus.ABANDONED,
            ExecutiveStrategyStatus.TERMINATED,
            ExecutiveStrategyStatus.SUPERSEDED,
            ExecutiveStrategyStatus.REJECTED,
            ExecutiveStrategyStatus.EXPIRED,
            ExecutiveStrategyStatus.INVALID,
        )
    
    @property
    def is_active(self) -> bool:
        """Check if strategy is currently active."""
        return self.status == ExecutiveStrategyStatus.ACTIVE
    
    # Validation methods
    def is_capacity_exceeded(self) -> Tuple[str, ...]:
        """Check if any capacity limits are exceeded."""
        violations = []
        if len(self.principles) > self.max_principles:
            violations.append("max_principles")
        if len(self.assumptions) > self.max_assumptions:
            violations.append("max_assumptions")
        if len(self.preconditions) > self.max_preconditions:
            violations.append("max_preconditions")
        if len(self.constraints) > self.max_constraints:
            violations.append("max_constraints")
        return tuple(violations)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStrategyId",
    "ExecutiveStrategyRevision",
    "ExecutiveStrategySubject",
    "ExecutiveStrategySubjectKind",
    "ExecutiveStrategyScope",
    "ExecutiveStrategyPurpose",
    "ExecutiveStrategyKind",
    "ExecutiveStrategyStatus",
    "ExecutiveStrategyActivationState",
    "ExecutiveStrategy",
)