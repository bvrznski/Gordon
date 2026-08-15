# Focusing Network Examples - Deterministic Fixtures
# =====================================================

"""
Deterministic fixture library for behavioral examples.

These fixtures provide reusable, deterministic data structures that:
- Use fixed UUIDs instead of random generation
- Use fixed timestamps for reproducibility
- Provide canonical example values

Usage:
    from gordon_system.examples.networks.focusing.fixtures import (
        ConversationFocusContext,
        TaskExecutionFocusContext,
        create_conversation_candidates,
        ...
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any

# Import Focusing contracts and models
from gordon_system.src.agent.components.networks.focusing.executive import (
    ProjectionId,
    AssessmentId,
    CorrelationId,
    CausationId,
    FocusMode,
    ObjectiveProjection,
    FocusCommitmentProjection,
    FocusPolicyConstraints,
    FocusResourceConstraints,
    ExecutiveFocusProjection,
    ExecutiveFocusDecisionKind,
    ExecutiveFocusDecision,
    FocusInteractionRecord,
)
from gordon_system.src.agent.components.networks.focusing.models import (
    FocusTargetId,
    CandidateId,
    FocusTarget,
    FocusCandidate,
    ProvenanceRecord,
)


# =============================================================================
# FIXED IDS - Deterministic instead of random UUID generation
# =============================================================================


class FixedIds:
    """Fixed ID values for deterministic fixtures."""
    
    # Projection IDs (fixed, not generated)
    PROJ_1 = ProjectionId(value="proj_fix000000000001")
    PROJ_2 = ProjectionId(value="proj_fix000000000002")
    PROJ_3 = ProjectionId(value="proj_fix000000000003")
    
    # Assessment IDs
    ASSESS_1 = AssessmentId(value="assess_fix0000000001")
    ASSESS_2 = AssessmentId(value="assess_fix0000000002")
    
    # Correlation IDs
    CORR_1 = CorrelationId(value="corr_fix000000000001")
    CORR_2 = CorrelationId(value="corr_fix000000000002")
    
    # Target IDs (for focus targets)
    TARGET_1 = FocusTargetId(value="target_fix000000000001")
    TARGET_2 = FocusTargetId(value="target_fix000000000002")
    TARGET_3 = FocusTargetId(value="target_fix000000000003")
    
    # Candidate IDs
    CANDIDATE_1 = CandidateId(value="candidate_fix0000000001")
    CANDIDATE_2 = CandidateId(value="candidate_fix0000000002")
    CANDIDATE_3 = CandidateId(value="candidate_fix0000000003")


# =============================================================================
# FIXED TIMESTAMP - Deterministic instead of datetime.utcnow()
# =============================================================================


FIXED_TIMESTAMP: datetime = datetime(2026, 8, 14, 10, 0, 0)


def fixed_timestamp() -> datetime:
    """Return the fixed timestamp for deterministic tests."""
    return FIXED_TIMESTAMP


# =============================================================================
# CONTEXT CLASSES - Reusable context structures
# =============================================================================


@dataclass(frozen=True)
class ConversationFocusContext:
    """
    Context for conversation focus examples.
    
    Represents a conversation thread where the agent must decide what to focus on
    while maintaining conversational continuity.
    """
    
    # Projection (from Executive to Focusing)
    projection: ExecutiveFocusProjection
    
    # Current focus commitment
    current_commitment: FocusCommitmentProjection
    
    # Conversation-related targets ( FocusTargets )
    conversation_targets: Tuple[FocusTarget, ...]
    
    # Candidate list for assessment
    candidates: Tuple[FocusCandidate, ...]
    
    @classmethod
    def create_conversation_context(
        cls,
        active_objective_id: str = "conv_obj_1",
        current_focus_target_id: str = "target_fix000000000001",
        current_focus_strength: float = 0.85,
    ) -> "ConversationFocusContext":
        """
        Create a conversation context with typical values.
        
        Args:
            active_objective_id: ID of the active conversation objective
            current_focus_target_id: ID of currently focused target
            current_focus_strength: Strength of focus commitment
            
        Returns:
            ConversationFocusContext instance
        """
        # Create projection from Executive to Focusing
        obj_proj = ObjectiveProjection(
            objective_id=active_objective_id,
            priority_hint=0.9,
            completion_status="in_progress",
        )
        
        projection = ExecutiveFocusProjection.create(
            active_objectives=(obj_proj,),
            revision=1,
        )
        
        # Create current commitment (what the conversation is focusing on)
        current_commitment = FocusCommitmentProjection(
            target_ids=(current_focus_target_id,),
            strength=current_focus_strength,
        )
        
        return cls(
            projection=projection.with_commitment(current_commitment),
            current_commitment=current_commitment,
            conversation_targets=tuple(),
            candidates=tuple(),
        )
    
    def with_candidates(self, candidates: Tuple[FocusCandidate, ...]) -> "ConversationFocusContext":
        """Create a copy with updated candidates."""
        return dataclass_replace(self, candidates=candidates)
    
    def with_conversation_targets(
        self,
        targets: Tuple[FocusTarget, ...],
    ) -> "ConversationFocusContext":
        """Create a copy with conversation targets."""
        return dataclass_replace(self, conversation_targets=targets)


@dataclass(frozen=True)
class TaskExecutionFocusContext:
    """
    Context for task execution focus examples.
    
    Represents an active task thread where the agent must decide what to focus on
    during task execution.
    """
    
    projection: ExecutiveFocusProjection
    current_commitment: FocusCommitmentProjection
    candidates: Tuple[FocusCandidate, ...]
    
    @classmethod
    def create_task_context(
        cls,
        active_objective_id: str = "task_obj_1",
        current_target_id: str = "target_fix000000000001",
        current_strength: float = 0.9,
    ) -> "TaskExecutionFocusContext":
        """Create a task execution context."""
        obj_proj = ObjectiveProjection(
            objective_id=active_objective_id,
            priority_hint=0.95,
            completion_status="in_progress",
        )
        
        projection = ExecutiveFocusProjection.create(
            active_objectives=(obj_proj,),
            revision=1,
        )
        
        current_commitment = FocusCommitmentProjection(
            target_ids=(current_target_id,),
            strength=current_strength,
        )
        
        return cls(
            projection=projection.with_commitment(current_commitment),
            current_commitment=current_commitment,
            candidates=tuple(),
        )
    
    def with_candidates(self, candidates: Tuple[FocusCandidate, ...]) -> "TaskExecutionFocusContext":
        """Create a copy with updated candidates."""
        return dataclass_replace(self, candidates=candidates)


# =============================================================================
# CANDIDATE CREATION FUNCTIONS
# =============================================================================


def create_conversation_candidates(
    context: ConversationFocusContext,
) -> Tuple[FocusCandidate, ...]:
    """
    Create conversation-related focus candidates.
    
    Candidates typically include:
    - Current participant input (highest priority)
    - Conversation objective (persistence)
    - Unresolved prior question
    - Delegated child Task result (if any)
    - Candidate response (deferred until processing input)
    - Unrelated internal reflection (suppressible)
    """
    # Create targets for candidates
    current_input_target = FocusTarget.create(
        semantic_category="participant_input",
        origin="conversation_stream",
        priority_hint=0.95,
        confidence=0.8,
        provenance=ProvenanceRecord.from_subsystem("conversation"),
    )
    
    conversation_continuity_target = FocusTarget.create(
        semantic_category="conversation_objective",
        origin="objective_system",
        priority_hint=0.75,
        confidence=0.9,
        provenance=ProvenanceRecord.from_subsystem("objectives"),
    )
    
    internal_maintenance_target = FocusTarget.create(
        semantic_category="internal_maintenance",
        origin="reflection_stream",
        priority_hint=0.3,  # Lower priority - can be suppressed
        confidence=0.6,
        provenance=ProvenanceRecord.from_subsystem("reflection"),
    )
    
    return (
        FocusCandidate(target=current_input_target),
        FocusCandidate(target=conversation_continuity_target),
        FocusCandidate(target=internal_maintenance_target),
    )


def create_task_execution_candidates(
    context: TaskExecutionFocusContext,
) -> Tuple[FocusCandidate, ...]:
    """
    Create task execution focus candidates.
    
    Candidates typically include:
    - Current plan step (primary)
    - Future plan steps (deferred)
    - Task evaluation (when appropriate)
    - Unrelated monitoring alert (low priority)
    - Documentation reference (optional)
    """
    current_step_target = FocusTarget.create(
        semantic_category="current_plan_step",
        origin="task_planning",
        priority_hint=0.9,
        confidence=0.85,
        provenance=ProvenanceRecord.from_subsystem("planning"),
    )
    
    future_step_target = FocusTarget.create(
        semantic_category="future_plan_step",
        origin="task_planning",
        priority_hint=0.4,  # Lower - will be deferred
        confidence=0.7,
        provenance=ProvenanceRecord.from_subsystem("planning"),
    )
    
    evaluation_target = FocusTarget.create(
        semantic_category="evaluation",
        origin="execution_monitoring",
        priority_hint=0.5,
        confidence=0.6,
        provenance=ProvenanceRecord.from_subsystem("monitoring"),
    )
    
    return (
        FocusCandidate(target=current_step_target),
        FocusCandidate(target=future_step_target),
        FocusCandidate(target=evaluation_target),
    )


# =============================================================================
# EXECUTIVE DECISION HELPERS
# =============================================================================


def create_executive_accept_decision(
    assessment_id: AssessmentId,
    projection_id: ProjectionId,
    accepted_targets: Tuple[str, ...],
    rationale: Optional[Tuple[str, ...]] = None,
) -> ExecutiveFocusDecision:
    """
    Create an ACCEPT_FOCUS_RECOMMENDATION decision.
    
    This represents the Executive layer accepting the Focusing Network's
    assessment recommendation as-is.
    """
    return ExecutiveFocusDecision.accept_recommendation(
        assessment_id=assessment_id,
        projection_id=projection_id,
        accepted_targets=accepted_targets,
        rationale=rationale or ("Assessment confidence meets acceptance threshold",),
    )


def create_executive_modify_decision(
    assessment_id: AssessmentId,
    projection_id: ProjectionId,
    accepted_targets: Tuple[str, ...],
    modifications: Optional[FocusPolicyConstraints] = None,
    rationale: Optional[Tuple[str, ...]] = None,
) -> ExecutiveFocusDecision:
    """
    Create an ACCEPT_WITH_MODIFICATION decision.
    
    This represents the Executive layer accepting with some modifications
    to the recommended targets or parameters.
    """
    return ExecutiveFocusDecision(
        decision_id=f"decision_fix_{assessment_id.value[-8:]}",
        assessment_id=assessment_id,
        projection_id=projection_id,
        decision_kind=ExecutiveFocusDecisionKind.ACCEPT_WITH_MODIFICATION,
        accepted_target_ids=accepted_targets,
        modified_targets=(
            FocusPolicyConstraints() if modifications is None else modifications
        ),
        rationale=rationale or ("Modified based on policy constraints",),
        timestamp_utc=fixed_timestamp(),
    )


def create_executive_preserve_decision(
    assessment_id: AssessmentId,
    projection_id: ProjectionId,
    rationale: Optional[Tuple[str, ...]] = None,
) -> ExecutiveFocusDecision:
    """
    Create a PRESERVE_CURRENT_FOCUS decision.
    
    This represents the Executive layer choosing to keep current focus
    despite different recommendations from Focusing.
    """
    return ExecutiveFocusDecision(
        decision_id=f"decision_fix_{assessment_id.value[-8:]}",
        assessment_id=assessment_id,
        projection_id=projection_id,
        decision_kind=ExecutiveFocusDecisionKind.PRESERVE_CURRENT_FOCUS,
        accepted_target_ids=tuple(),
        rationale=rationale or ("Current focus stability outweighs recommendation",),
        timestamp_utc=fixed_timestamp(),
    )


def create_executive_reject_decision(
    assessment_id: AssessmentId,
    projection_id: ProjectionId,
    rejection_reasons: Tuple[str, ...],
) -> ExecutiveFocusDecision:
    """
    Create a REJECT_RECOMMENDATION decision.
    
    This represents the Executive layer rejecting the Focusing Network's
    assessment recommendation entirely.
    """
    return ExecutiveFocusDecision(
        decision_id=f"decision_fix_{assessment_id.value[-8:]}",
        assessment_id=assessment_id,
        projection_id=projection_id,
        decision_kind=ExecutiveFocusDecisionKind.REJECT_RECOMMENDATION,
        rejected_target_ids=tuple(),
        rationale=rejection_reasons,
        timestamp_utc=fixed_timestamp(),
    )


# =============================================================================
# INTERACTION RECORD HELPERS
# =============================================================================


def create_interaction_record(
    projection: ExecutiveFocusProjection,
    assessment_id: AssessmentId,
    recommended_targets: Tuple[str, ...],
) -> FocusInteractionRecord:
    """
    Create a focus interaction record for observational tracking.
    
    This is purely observational - it does not become authoritative state
    for either system. It exists solely for diagnostics and debugging.
    """
    return FocusInteractionRecord.from_projection_and_assessment(
        projection=projection,
        assessment_id=assessment_id,
        recommended_targets=recommended_targets,
    )


# =============================================================================
# UTILITY FUNCTIONS
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
# EXAMPLE SCENARIO CONTEXTS
# =============================================================================


def create_conversation_focus_scenario() -> Tuple[
    ConversationFocusContext,
    Tuple[FocusCandidate, ...],
]:
    """
    Create context for Example A - Conversation Focus.
    
    Scenario: A ConversationThread is active. The participant asks a complex
    question that requires interpretation before a response can be produced.
    
    Expected Focusing behavior:
        • prioritize the current participant input
        • maintain the conversation objective as a persistent secondary context
        • suppress unrelated internal reflection
        • recommend sufficient precision for reference resolution
        • recommend retaining unresolved commitments in secondary focus
    """
    context = ConversationFocusContext.create_conversation_context(
        active_objective_id="conv_obj_complex_question",
    )
    
    candidates = create_conversation_candidates(context)
    context = context.with_candidates(candidates)
    
    return context, candidates


def create_task_execution_focus_scenario() -> Tuple[
    TaskExecutionFocusContext,
    Tuple[FocusCandidate, ...],
]:
    """
    Create context for Example E - Task Execution Focus.
    
    Scenario: A TaskThread has an accepted plan and one executable next action.
    
    Expected Focusing behavior:
        • current executable step becomes primary
        • task objective remains secondary persistent context
        • future steps remain deferred
        • evaluation receives readiness only after execution evidence exists
    """
    context = TaskExecutionFocusContext.create_task_context(
        active_objective_id="task_obj_execution",
    )
    
    candidates = create_task_execution_candidates(context)
    context = context.with_candidates(candidates)
    
    return context, candidates


__all__ = [
    # Fixed IDs
    "FixedIds",
    "FIXED_TIMESTAMP",
    "fixed_timestamp",
    
    # Context classes
    "ConversationFocusContext",
    "TaskExecutionFocusContext",
    
    # Candidate creation functions
    "create_conversation_candidates",
    "create_task_execution_candidates",
    
    # Executive decision helpers
    "create_executive_accept_decision",
    "create_executive_modify_decision",
    "create_executive_preserve_decision",
    "create_executive_reject_decision",
    
    # Interaction record helper
    "create_interaction_record",
    
    # Scenario context creators
    "create_conversation_focus_scenario",
    "create_task_execution_focus_scenario",
]