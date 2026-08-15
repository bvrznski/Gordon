# Focusing Network Executive Interaction Contracts - Phase 4.2.9
# ================================================================

"""
Executive interaction contracts for the FocusingNetwork.

This package establishes the architectural boundaries between:

    EXECUTIVE (authoritative) → FOCUSING (computational)

The Focusing Network computes focus recommendations.
The Executive layer interprets those recommendations authoritatively.

ARCHITECTURAL PRINCIPLES:
========================

Computational vs Authoritative:
    - Focusing estimates goal-directed attentional demand
    - Executive decides how that demand affects behavior
    
Immutable Input, Advisory Output:
    - Executive projections are immutable (no mutation)
    - FocusAssessment is advisory (not binding)

Ownership Separation:
    - Executive owns: goals, commitments, policy, behavioral decisions
    - Focusing owns: candidate evaluation, priority estimation, competition analysis

BEHAVIORAL BOUNDARY:
===================

Executive → Focusing Input (Immutable Projections):
    • Active objectives (what goals are active)
    • Objective hierarchy (priority order)
    • Current commitment (focus state)
    • Task criticality (urgency context)
    • Strategy context (plan context)
    • Policy constraints (rules to follow)
    • Resource constraints (budget limits)
    • Allowed focus modes ( permitted modes)
    • Interruption cost (cost of switching)
    • Deadline pressure (time sensitivity)

Focusing → Executive Output (Advisory Assessment):
    • Recommended primary target
    • Secondary targets
    • Precision recommendation
    • Persistence recommendation  
    • Suppression recommendation
    • Bias recommendation
    • Resource-demand estimate
    • Confidence level
    • Explanation (why these recommendations)
    • Stability information

Executive Decisions (NOT from Focusing):
    • ACCEPT_FOCUS_RECOMMENDATION
    • ACCEPT_WITH_MODIFICATION
    • PRESERVE_CURRENT_FOCUS
    • DEFER_FOCUS_CHANGE
    • REQUEST_REASSESSMENT
    • DIVIDE_FOCUS
    • RELEASE_FOCUS
    • REJECT_RECOMMENDATION

VERSION: 1.0.0
COMPATIBILITY: backward
DEPRECATION: three_releases policy
EXTENSION STRATEGY: additive_only
"""

from dataclasses import dataclass, field
from typing import (
    Optional,
    Tuple,
    Dict,
    Any,
    Literal,
)
from datetime import datetime
import uuid

# =============================================================================
# IDENTITY TYPES - Executive interaction events
# =============================================================================


@dataclass(frozen=True)
class ProjectionId:
    """Unique identifier for an executive projection."""
    value: str = field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "ProjectionId":
        return cls(value=f"proj_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class AssessmentId:
    """Unique identifier for a focus assessment."""
    value: str = field(default_factory=lambda: f"assess_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "AssessmentId":
        return cls(value=f"assess_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class CorrelationId:
    """Identifier for correlating related events."""
    value: str = field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "CorrelationId":
        return cls(value=f"corr_{uuid.uuid4().hex[:16]}")


@dataclass(frozen=True)
class CausationId:
    """Identifier for causal chain tracking."""
    value: str = field(default_factory=lambda: f"cause_{uuid.uuid4().hex[:16]}")
    
    @classmethod
    def generate(cls) -> "CausationId":
        return cls(value=f"cause_{uuid.uuid4().hex[:16]}")


# =============================================================================
# FOCUS MODE - Permitted focus allocation modes
# =============================================================================


class FocusMode:
    """Focus allocation mode."""
    SINGLE_TARGET = "single_target"
    DIVIDED_TARGET = "divided_target"
    MONITORING = "monitoring"
    
    ALL = (SINGLE_TARGET, DIVIDED_TARGET, MONITORING)


# =============================================================================
# EXECUTIVE FOCUS PROJECTION - Immutable input from Executive to Focusing
# =============================================================================


@dataclass(frozen=True)
class ObjectiveProjection:
    """
    Projection of a single objective for focus allocation.
    
    This represents ONE objective that the executive considers active.
    It is NOT an ordered hierarchy - ordering is external to this projection.
    """
    objective_id: str
    """Unique identifier for the objective."""
    
    priority_hint: Optional[float] = None
    """Priority hint from external sources (0.0 to 1.0)."""
    
    deadline_utc: Optional[datetime] = None
    """Optional deadline for this objective."""
    
    completion_status: Optional[str] = None
    """Completion status (e.g., 'in_progress', 'pending', 'completed')."""
    
    context: Dict[str, Any] = field(default_factory=dict)
    """Additional contextual information."""


@dataclass(frozen=True)
class FocusCommitmentProjection:
    """
    Projection of current focus commitment state.
    
    This represents the executive's currently accepted focus configuration,
    without ownership of that commitment itself.
    """
    target_ids: Tuple[str, ...]
    """IDs of targets currently committed to focus."""
    
    strength: float = 0.5
    """Commitment strength (0.0 to 1.0)."""
    
    estimated_completion_seconds: Optional[float] = None
    """Estimated time until current focus completes."""
    
    last_update_utc: Optional[datetime] = field(default_factory=datetime.utcnow)
    """When this commitment was last updated."""


@dataclass(frozen=True)
class FocusPolicyConstraints:
    """
    Policy constraints that must be respected by Focusing.
    
    These are rules the computational engine must follow, but they do not
    constitute policy authority - that remains with Executive.
    """
    max_concurrent_targets: int = 3
    """Maximum concurrent focus targets allowed."""
    
    min_precision_threshold: float = 0.1
    """Minimum precision for any allocated target."""
    
    allow_focus_division: bool = False
    """Whether divided focus is permitted."""
    
    prohibit_suppression_of_types: Tuple[str, ...] = field(default_factory=tuple)
    """Focus types that may never be suppressed (e.g., 'safety_monitor')."""
    
    resource_budget_limit: float = 1.0
    """Maximum resource budget percentage (0.0 to 1.0)."""


@dataclass(frozen=True)
class FocusResourceConstraints:
    """
    Resource constraints for focus allocation.
    
    These define limits that Focusing must respect when estimating resource demands.
    """
    available_threads: int = 4
    """Available computational threads."""
    
    max_cpu_percent: float = 80.0
    """Maximum CPU percentage that may be allocated to focus."""
    
    memory_limit_mb: int = 4096
    """Memory limit for focus-related operations."""
    
    timeout_seconds: Optional[float] = None
    """Timeout for focus computations."""


@dataclass(frozen=True)
class ExecutiveFocusProjection:
    """
    Immutable projection of executive state for Focusing computation.
    
    This is the INPUT to the FocusingNetwork. It contains all information
    that Executive wants Focusing to consider when computing recommendations.
    
    PROPERTIES:
        • Immutable once created (frozen dataclass)
        • Revision-tracked (for stale assessment detection)
        • Serialization-ready (JSON-compatible)
        • No runtime references (no callbacks, no threads, no schedulers)
    
    EXECUTIVE OWNS:
        • Active objectives
        • Objective hierarchy ordering
        • Commitment decisions
        • Policy definition
        • Strategy selection
    
    FOCUSING MAY USE (but does NOT own):
        • Projections of the above for computational context
        • Estimates based on these projections
        
    NEVER PASS:
        • Executive controller instance
        • Live callback references
        • Runtime scheduling objects
        • Concrete thread/loop instances
    """
    
    # Projection identity and versioning (required fields - no defaults)
    projection_id: ProjectionId
    """Unique identifier for this projection."""
    
    revision: int
    """Revision number (incremented on state changes)."""
    
    timestamp_utc: datetime
    """When this projection was created."""
    
    # Active objectives (Executive-owned, Focusing reads only) - required fields first
    active_objectives: Tuple[ObjectiveProjection, ...]
    """Currently active objectives."""
    
    # Current commitment state - required before optional fields
    current_commitment: FocusCommitmentProjection
    """Current focus commitment projection."""
    
    objective_hierarchy: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered list of objective IDs by priority (Executive hierarchy)."""
    
    # Decision context (optional - has defaults)
    task_criticality: float = 0.5
    """Current task criticality (0.0 to 1.0)."""
    
    strategy_context: str = ""
    """Strategy context string (e.g., 'exploration', 'exploitation')."""
    
    policy_constraints: FocusPolicyConstraints = field(default_factory=FocusPolicyConstraints)
    """Policy constraints for focus allocation."""
    
    resource_constraints: FocusResourceConstraints = field(default_factory=FocusResourceConstraints)
    """Resource constraints for focus allocation."""
    
    allowed_focus_modes: Tuple[str, ...] = field(default_factory=lambda: tuple(FocusMode.ALL))
    """Focus modes permitted by Executive."""
    
    interruption_cost: Optional[float] = None
    """Estimated cost of interrupting current focus."""
    
    deadline_pressure: Optional[float] = None
    """Deadline pressure indicator (0.0 to 1.0)."""
    
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)
    """For correlating related events."""
    
    causation_id: Optional[CausationId] = None
    """For causal chain tracking."""
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    """Provenance information about this projection."""
    
    external_context: Dict[str, Any] = field(default_factory=dict)
    """Any additional context from external systems."""
    
    @classmethod
    def create(
        cls,
        active_objectives: Tuple[ObjectiveProjection, ...],
        revision: int = 1,
        timestamp_utc: Optional[datetime] = None,
        current_commitment: Optional[FocusCommitmentProjection] = None,
    ) -> "ExecutiveFocusProjection":
        """
        Create a new executive focus projection.
        
        Args:
            active_objectives: Currently active objectives
            revision: Projection revision number (increment on state changes)
            timestamp_utc: Timestamp for this projection (auto-generated if not provided)
            current_commitment: Current focus commitment if any
            
        Returns:
            New ExecutiveFocusProjection instance
        """
        return cls(
            projection_id=ProjectionId.generate(),
            revision=revision,
            timestamp_utc=timestamp_utc or datetime.utcnow(),
            active_objectives=active_objectives,
            current_commitment=current_commitment or FocusCommitmentProjection(target_ids=tuple()),
        )
    
    def with_revision(self, new_revision: int) -> "ExecutiveFocusProjection":
        """Create a copy with updated revision number."""
        return dataclass_replace(self, revision=new_revision)
    
    def with_timestamp(self, timestamp_utc: datetime) -> "ExecutiveFocusProjection":
        """Create a copy with updated timestamp."""
        return dataclass_replace(self, timestamp_utc=timestamp_utc)
    
    def with_commitment(self, commitment: FocusCommitmentProjection) -> "ExecutiveFocusProjection":
        """Create a copy with updated commitment projection."""
        return dataclass_replace(self, current_commitment=commitment)


# =============================================================================
# FOCUS ASSESSMENT APPLICATION RESULT - Result of applying an assessment
# =============================================================================


@dataclass(frozen=True)
class FocusDecisionModification:
    """
    Description of modifications made to a focus recommendation.
    
    This captures how Executive adjusted the computational recommendations
    before accepting them as commitments.
    """
    precision_adjustment: Optional[float] = None
    """Adjustment to recommended precision."""
    
    target_modifications: Tuple[str, ...] = field(default_factory=tuple)
    """Target IDs that were added/removed."""
    
    priority_modification: Optional[float] = None
    """Adjustment to priority weights."""
    
    reason: Optional[str] = None
    """Explanation for modifications."""


@dataclass(frozen=True)
class ExecutiveFocusDecisionKind:
    """
    Kinds of executive decisions about focus recommendations.
    
    These represent AUTHORITY decisions made by Executive, not Focusing.
    Focusing may estimate these as advisory categories but never makes them.
    """
    # Acceptance decisions
    ACCEPT_FOCUS_RECOMMENDATION = "accept_focus_recommendation"
    """Accept the recommendation as-is."""
    
    ACCEPT_WITH_MODIFICATION = "accept_with_modification"
    """Accept with modifications to recommended targets or parameters."""
    
    PRESERVE_CURRENT_FOCUS = "preserve_current_focus"
    """Keep current focus despite different recommendations."""
    
    # Deferral decisions
    DEFER_FOCUS_CHANGE = "defer_focus_change"
    """Postpone focus change until later."""
    
    REQUEST_REASSESSMENT = "request_reassessment"
    """Request updated assessment with more information."""
    
    REQUEST_ADDITIONAL_CONTEXT = "request_additional_context"
    """Request additional context before deciding."""
    
    # Divided focus decisions
    DIVIDE_FOCUS = "divide_focus"
    """Allow divided focus across multiple targets."""
    
    # Release decisions
    RELEASE_FOCUS = "release_focus"
    """Release current focus commitment."""
    
    # Rejection decisions
    REJECT_RECOMMENDATION = "reject_recommendation"
    """Reject the recommendation entirely."""


@dataclass(frozen=True)
class ExecutiveFocusDecision:
    """
    Authoritative decision about focus from Executive.
    
    This is NOT produced by FocusingNetwork. It represents a commitment
    decision made by Executive based on FocusAssessment inputs.
    
    EXECUTIVE OWNS this decision. Focusing may only observe it as feedback.
    """
    
    # Identity - required fields first (no defaults)
    assessment_id: AssessmentId
    """Assessment that this decision responds to."""
    
    projection_id: ProjectionId
    """Projection revision that this decision applies to."""
    
    decision_kind: str  # Use ExecutiveFocusDecisionKind values
    """What kind of decision was made."""
    
    # Optional fields with defaults (must come after required)
    decision_id: str = field(default_factory=lambda: f"decision_{uuid.uuid4().hex[:16]}")
    """Unique identifier for this decision."""
    
    accepted_target_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Target IDs that were accepted for focus."""
    
    rejected_target_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Target IDs that were rejected."""
    
    modified_targets: Optional[FocusDecisionModification] = None
    """Modifications made to recommendations before acceptance."""
    
    rationale: Tuple[str, ...] = field(default_factory=tuple)
    """Rationale for this decision (policy reasons, etc.)."""
    
    resulting_commitment: Optional[FocusCommitmentProjection] = None
    """Resulting focus commitment after decision."""
    
    timestamp_utc: datetime = field(default_factory=datetime.utcnow)
    """When this decision was made."""
    
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)
    """For correlating with assessment."""
    
    causation_id: Optional[CausationId] = None
    """Causal chain reference."""
    
    @classmethod
    def accept_recommendation(
        cls,
        assessment_id: AssessmentId,
        projection_id: ProjectionId,
        decision_kind: str = ExecutiveFocusDecisionKind.ACCEPT_FOCUS_RECOMMENDATION,
        accepted_targets: Tuple[str, ...] = tuple(),
        rationale: Optional[Tuple[str, ...]] = None,
    ) -> "ExecutiveFocusDecision":
        """Create an ACCEPT_FOCUS_RECOMMENDATION decision."""
        return cls(
            assessment_id=assessment_id,
            projection_id=projection_id,
            decision_kind=decision_kind,
            accepted_target_ids=accepted_targets,
            rationale=rationale or tuple(),
        )
    
    def is_accepted(self) -> bool:
        """Check if the recommendation was accepted."""
        return self.decision_kind in {
            ExecutiveFocusDecisionKind.ACCEPT_FOCUS_RECOMMENDATION,
            ExecutiveFocusDecisionKind.ACCEPT_WITH_MODIFICATION,
        }
    
    def is_rejected(self) -> bool:
        """Check if the recommendation was rejected."""
        return self.decision_kind == ExecutiveFocusDecisionKind.REJECT_RECOMMENDATION
    
    def is_deferred(self) -> bool:
        """Check if the change was deferred."""
        return self.decision_kind in {
            ExecutiveFocusDecisionKind.DEFER_FOCUS_CHANGE,
            ExecutiveFocusDecisionKind.REQUEST_REASSESSMENT,
            ExecutiveFocusDecisionKind.REQUEST_ADDITIONAL_CONTEXT,
        }


@dataclass(frozen=True)
class FocusInteractionRecord:
    """
    Immutable record of an interaction between Executive and Focusing.
    
    This is observational - it does not become authoritative state for
    either system. It exists solely for diagnostics, audit, and debugging.
    """
    
    # Identity - required fields first (no defaults)
    projection_id: ProjectionId
    projection_revision: int
    
    assessment_id: AssessmentId
    assessment_computation_version: str = "1.0"
    
    correlation_id: CorrelationId = field(default_factory=CorrelationId.generate)
    
    # Optional fields with defaults (must come after required)
    interaction_id: str = field(default_factory=lambda: f"interaction_{uuid.uuid4().hex[:16]}")
    
    decision_id: Optional[str] = None
    decision_kind: Optional[str] = None
    decision_timestamp_utc: Optional[datetime] = None
    
    recommended_targets: Tuple[str, ...] = field(default_factory=tuple)
    accepted_targets: Tuple[str, ...] = field(default_factory=tuple)
    rejected_targets: Tuple[str, ...] = field(default_factory=tuple)
    
    causation_id: Optional[CausationId] = None
    
    projection_created_utc: datetime = field(default_factory=datetime.utcnow)
    assessment_computed_utc: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_projection_and_assessment(
        cls,
        projection: ExecutiveFocusProjection,
        assessment_id: AssessmentId,
        recommended_targets: Tuple[str, ...],
    ) -> "FocusInteractionRecord":
        """Create a record when Focusing receives a projection and produces an assessment."""
        return cls(
            projection_id=projection.projection_id,
            projection_revision=projection.revision,
            assessment_id=assessment_id,
            recommended_targets=recommended_targets,
            correlation_id=projection.correlation_id,
        )
    
    def with_decision(self, decision: ExecutiveFocusDecision) -> "FocusInteractionRecord":
        """Create a copy with decision information added."""
        return dataclass_replace(
            self,
            decision_id=decision.decision_id,
            decision_kind=decision.decision_kind,
            decision_timestamp_utc=decision.timestamp_utc,
            accepted_targets=decision.accepted_target_ids,
            rejected_targets=decision.rejected_target_ids,
        )


@dataclass(frozen=True)
class FocusAssessmentApplicationResult:
    """
    Result of attempting to apply a FocusAssessment.
    
    This is produced by Executive (not Focusing) when evaluating whether
    and how to apply an assessment from the computational network.
    """
    
    # Status
    is_valid: bool = True
    """Is this assessment valid for application?"""
    
    is_stale: bool = False
    """Does this assessment use outdated projection revision?"""
    
    is_compatible: bool = True
    """Is this assessment compatible with current executive state?"""
    
    # Validation details
    validation_errors: Tuple[str, ...] = field(default_factory=tuple)
    """Any validation errors found."""
    
    staleness_reason: Optional[str] = None
    """Explanation of why stale (if stale)."""
    
    # Action taken
    action_taken: Literal["applied", "rejected", "deferred"] = "applied"
    """What action was taken on this assessment."""
    
    # Resulting state (after application)
    resulting_commitment: Optional[FocusCommitmentProjection] = None
    
    # Timestamps
    assessed_at_utc: datetime = field(default_factory=datetime.utcnow)
    applied_at_utc: Optional[datetime] = None
    
    @classmethod
    def valid_and_applied(
        cls,
        resulting_commitment: FocusCommitmentProjection,
    ) -> "FocusAssessmentApplicationResult":
        """Create a result indicating valid assessment was applied."""
        return cls(
            is_valid=True,
            is_stale=False,
            is_compatible=True,
            action_taken="applied",
            resulting_commitment=resulting_commitment,
            applied_at_utc=datetime.utcnow(),
        )
    
    @classmethod
    def stale(
        cls,
        expected_revision: int,
        actual_revision: int,
        reason: Optional[str] = None,
    ) -> "FocusAssessmentApplicationResult":
        """Create a result indicating assessment is stale."""
        return cls(
            is_valid=False,
            is_stale=True,
            validation_errors=(f"Projection revision mismatch: expected {expected_revision}, got {actual_revision}",),
            staleness_reason=reason or f"Projection was at revision {expected_revision}, assessment used revision {actual_revision}",
            action_taken="deferred",
        )
    
    @classmethod
    def incompatible(
        cls,
        errors: Tuple[str, ...],
    ) -> "FocusAssessmentApplicationResult":
        """Create a result indicating assessment is incompatible."""
        return cls(
            is_valid=False,
            is_compatible=False,
            validation_errors=errors,
            action_taken="rejected",
        )
    
    def is_application_allowed(self) -> bool:
        """Check if this assessment may be applied."""
        return self.is_valid and not self.is_stale and self.is_compatible


# =============================================================================
# UTILITY: dataclass_replace for frozen dataclasses
# =============================================================================


def dataclass_replace(obj: Any, **kwargs) -> Any:
    """
    Replace fields in a frozen dataclass instance.
    
    Creates a new copy with specified fields updated while maintaining
    immutability guarantees.
    """
    if hasattr(obj, "__dataclass_fields__"):
        field_dict = {
            f.name: getattr(obj, f.name)
            for f in obj.__dataclass_fields__.values()
        }
        field_dict.update(kwargs)
        return type(obj)(**field_dict)
    raise TypeError(f"Object {obj} is not a dataclass")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "ProjectionId",
    "AssessmentId", 
    "CorrelationId",
    "CausationId",
    
    # Focus mode constants
    "FocusMode",
    
    # Projections (Executive → Focusing input)
    "ObjectiveProjection",
    "FocusCommitmentProjection",
    "FocusPolicyConstraints",
    "FocusResourceConstraints",
    "ExecutiveFocusProjection",
    
    # Assessment application results (Executive evaluation of Focusing output)
    "FocusAssessmentApplicationResult",
    "FocusDecisionModification",
    "ExecutiveFocusDecisionKind",
    "ExecutiveFocusDecision",
    
    # Interaction records (observational)
    "FocusInteractionRecord",
    
    # Utilities
    "dataclass_replace",
]