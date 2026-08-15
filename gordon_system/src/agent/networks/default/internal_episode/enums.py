# Internal Episode Enums and Canonical Vocabulary
# ================================================

"""
Canonical vocabulary for the InternalEpisode model.

This module defines:
    - Episode types (categories of internal cognition)
    - Episode purposes (concrete reasons for episode instances)
    - Episode scope constraints
    - Lifecycle states
    - Requester categories
    - Capability categories
    - Evidence categories
    - Outcome kinds
    - Continuation recommendations
    - Relationship kinds

ARCHITECTURAL PRINCIPLES:
    - Immutable enum values
    - Deterministic ordering where applicable
    - Bounded sets (no unbounded expansion)
    - No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, FrozenSet
from datetime import timedelta


# =============================================================================
# EPISODE TYPE - Categories of internal cognition
# =============================================================================

class InternalEpisodeType:
    """
    Canonical categories for internally generated cognitive coordination.
    
    Type describes the COGNITIVE CATEGORY, not the implementation algorithm.
    
    Each type has:
        - Canonical meaning (what kind of cognition)
        - Expected context purpose (what context is needed)
        - Allowed request kinds
        - Possible outcome kinds
        - Scope expectations
        - Validation profile
        - Allowed child-episode relationships
    """
    
    # Reflection and self-analysis
    REFLECTION = "reflection"
    """Review prior activity and derive insight."""
    
    FUTURE_SIMULATION = "future_simulation"
    """Explore possible future outcomes."""
    
    COUNTERFACTUAL_ANALYSIS = "counterfactual_analysis"
    """Examine alternatives to observed or expected events."""
    
    NARRATIVE_INTEGRATION = "narrative_integration"
    """Relate new experience to continuity and identity."""
    
    IDENTITY_INTEGRATION = "identity_integration"
    """Process identity tensions and continuity."""
    
    MEMORY_INTEGRATION = "memory_integration"
    """Consolidate and associate memories."""
    
    PREDICTIVE_REVIEW = "predictive_review"
    """Review predictive models against outcomes."""
    
    PROBLEM_INCUBATION = "problem_incubation"
    """Background problem solving without active effort."""
    
    CREATIVE_SYNTHESIS = "creative_synthesis"
    """Combine disparate ideas into novel solutions."""
    
    SELF_EVALUATION = "self_evaluation"
    """Assess internal consistency or performance."""
    
    CONCERN_REVIEW = "concern_review"
    """Review unresolved concerns and pending issues."""
    
    INSIGHT_INTEGRATION = "insight_integration"
    """Integrate new insights into existing models."""
    
    WORKSPACE_CANDIDATE_PREPARATION = "workspace_candidate_preparation"
    """Prepare candidates for conscious workspace submission."""
    
    GENERAL_INTERNAL_COGNITION = "general_internal_cognition"
    """General internal coordination without specific type."""
    
    @classmethod
    def all_types(cls) -> Tuple[str, ...]:
        """Return all valid episode type values."""
        return (
            cls.REFLECTION,
            cls.FUTURE_SIMULATION,
            cls.COUNTERFACTUAL_ANALYSIS,
            cls.NARRATIVE_INTEGRATION,
            cls.IDENTITY_INTEGRATION,
            cls.MEMORY_INTEGRATION,
            cls.PREDICTIVE_REVIEW,
            cls.PROBLEM_INCUBATION,
            cls.CREATIVE_SYNTHESIS,
            cls.SELF_EVALUATION,
            cls.CONCERN_REVIEW,
            cls.INSIGHT_INTEGRATION,
            cls.WORKSPACE_CANDIDATE_PREPARATION,
            cls.GENERAL_INTERNAL_COGNITION,
        )
    
    @classmethod
    def requires_memory(cls, episode_type: str) -> bool:
        """Check if a type typically requires memory context."""
        required = {
            cls.REFLECTION,
            cls.NARRATIVE_INTEGRATION,
            cls.IDENTITY_INTEGRATION,
            cls.MEMORY_INTEGRATION,
            cls.PROBLEM_INCUBATION,
            cls.CREATIVE_SYNTHESIS,
            cls.CONCERN_REVIEW,
        }
        return episode_type in required
    
    @classmethod
    def requires_prediction(cls, episode_type: str) -> bool:
        """Check if a type typically requires predictive context."""
        required = {
            cls.FUTURE_SIMULATION,
            cls.COUNTERFACTUAL_ANALYSIS,
            cls.PREDICTIVE_REVIEW,
        }
        return episode_type in required
    
    @classmethod
    def produces_insights(cls, episode_type: str) -> bool:
        """Check if a type typically produces insights."""
        return episode_type in {
            cls.REFLECTION,
            cls.CREATIVE_SYNTHESIS,
            cls.SELF_EVALUATION,
            cls.PREDICTIVE_REVIEW,
        }


# =============================================================================
# EPISODE REQUESTER - Origins of internal coordination requests
# =============================================================================

class InternalEpisodeRequester:
    """
    Categories of sources that request internal cognitive episodes.
    
    The requester identifies origin but does NOT imply ownership authority.
    The Default Network validates and owns episode lifecycle.
    """
    
    EXECUTIVE_PROJECTION = "executive_projection"
    """Projection from executive system requiring coordination."""
    
    INTERNAL_THREAD = "internal_thread"
    """Internally generated thread initiation."""
    
    DEFAULT_NETWORK = "default_network"
    """Initiated by DefaultNetwork itself."""
    
    REFLECTION_RESULT = "reflection_result"
    """Triggered by previous reflection episode result."""
    
    PREDICTIVE_RESULT = "predictive_result"
    """Triggered by predictive network result."""
    
    MEMORY_RESULT = "memory_result"
    """Triggered by memory system result."""
    
    NARRATIVE_RESULT = "narrative_result"
    """Triggered by narrative coordination result."""
    
    WORKSPACE_FEEDBACK = "workspace_feedback"
    """Feedback from conscious workspace processing."""
    
    UNRESOLVED_CONCERN = "unresolved_concern"
    """Triggered by unresolved concern detection."""
    
    EXTERNAL_REQUEST_PROJECTION = "external_request_projection"
    """Projection of external request requiring internal processing."""
    
    UNKNOWN = "unknown"
    """Origin cannot be determined."""
    
    @classmethod
    def all_requesters(cls) -> Tuple[str, ...]:
        """Return all valid requester values."""
        return (
            cls.EXECUTIVE_PROJECTION,
            cls.INTERNAL_THREAD,
            cls.DEFAULT_NETWORK,
            cls.REFLECTION_RESULT,
            cls.PREDICTIVE_RESULT,
            cls.MEMORY_RESULT,
            cls.NARRATIVE_RESULT,
            cls.WORKSPACE_FEEDBACK,
            cls.UNRESOLVED_CONCERN,
            cls.EXTERNAL_REQUEST_PROJECTION,
            cls.UNKNOWN,
        )


# =============================================================================
# EPISODE LIFECYCLE STATES - Semantic coordination states
# =============================================================================

class InternalEpisodeLifecycle:
    """
    Canonical lifecycle states for internal episodes.
    
    These represent semantic coordination state, NOT runtime execution state.
    Core and Execution handle actual runtime mechanics.
    """
    
    # Pre-active states
    PROPOSED = "proposed"
    """Request exists but has not been validated."""
    
    VALIDATED = "validated"
    """Request, purpose, scope, and context binding are valid."""
    
    READY = "ready"
    """Episode may be processed when Execution and Core permit."""
    
    # Active states
    ACTIVE = "active"
    """Bounded episode progression is currently being coordinated."""
    
    WAITING_FOR_INPUT = "waiting_for_input"
    """Required projected information is unavailable."""
    
    WAITING_FOR_CAPABILITY = "waiting_for_capability"
    """Capability request issued, result pending."""
    
    SUSPENDED = "suspended"
    """Processing intentionally paused but valid."""
    
    COMPLETING = "completing"
    """Outcome composition or final validation in progress."""
    
    # Terminal states
    COMPLETED = "completed"
    """Valid terminal outcome produced."""
    
    FAILED = "failed"
    """Terminated without valid successful outcome."""
    
    CANCELLED = "cancelled"
    """Terminated by authority before normal completion."""
    
    EXPIRED = "expired"
    """Context, scope, or deadline expired."""
    
    SUPERSEDED = "superseded"
    """Newer episode replaced this episode's purpose or authority."""
    
    @classmethod
    def is_pre_active(cls, state: str) -> bool:
        """Check if state is pre-active (before processing begins)."""
        return state in {cls.PROPOSED, cls.VALIDATED, cls.READY}
    
    @classmethod
    def is_active(cls, state: str) -> bool:
        """Check if state is active (during processing)."""
        return state in {
            cls.ACTIVE,
            cls.WAITING_FOR_INPUT,
            cls.WAITING_FOR_CAPABILITY,
            cls.SUSPENDED,
            cls.COMPLETING,
        }
    
    @classmethod
    def is_terminal(cls, state: str) -> bool:
        """Check if state is terminal (processing ended)."""
        return state in {cls.COMPLETED, cls.FAILED, cls.CANCELLED, cls.EXPIRED, cls.SUPERSEDED}
    
    @classmethod
    def all_states(cls) -> Tuple[str, ...]:
        """Return all valid lifecycle states."""
        return (
            cls.PROPOSED,
            cls.VALIDATED,
            cls.READY,
            cls.ACTIVE,
            cls.WAITING_FOR_INPUT,
            cls.WAITING_FOR_CAPABILITY,
            cls.SUSPENDED,
            cls.COMPLETING,
            cls.COMPLETED,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
            cls.SUPERSEDED,
        )


# =============================================================================
# LIFECYCLE TRANSITION REASONS - Why state changes occur
# =============================================================================

class LifecycleTransitionReason:
    """
    Standard reasons for lifecycle state transitions.
    
    These provide explicit justification for state changes without
    embedding runtime implementation details.
    """
    
    # Validation and preparation
    REQUEST_RECEIVED = "request_received"
    """Initial request received."""
    
    VALIDATION_COMPLETE = "validation_complete"
    """Request, purpose, scope validated successfully."""
    
    CONTEXT_AVAILABLE = "context_available"
    """Required context projections became available."""
    
    # Activation and progression
    EXECUTION_PERMITTED = "execution_permitted"
    """Execution resources allocated."""
    
    STEP_STARTED = "step_started"
    """Plan step began processing."""
    
    CAPABILITY_REQUESTED = "capability_requested"
    """Capability request issued to owner."""
    
    # Waiting states
    INPUT_MISSING = "input_missing"
    """Required projected information unavailable."""
    
    CAPABILITY_PENDING = "capability_pending"
    """Waiting for capability result."""
    
    # Suspension and resumption
    RESOURCE_CONSTRAINT = "resource_constraint"
    """Resource constraints prevent useful progress."""
    
    HIGHER_PRIORITY = "higher_priority"
    """Stronger semantic activity takes precedence."""
    
    SUSPENDED_REQUESTED = "suspended_requested"
    """Explicit suspension requested."""
    
    CONTEXT_REFRESH_REQUIRED = "context_refresh_required"
    """Context stale or invalid, requires refresh."""
    
    # Completion
    OUTCOME_PRODUCED = "outcome_produced"
    """Valid outcome produced and validated."""
    
    ALL_STEPS_COMPLETE = "all_steps_complete"
    """All plan steps completed successfully."""
    
    # Terminal states
    FAILURE_OCCURRED = "failure_occurred"
    """Processing failed with no recoverable path."""
    
    CAPABILITY_FAILURE = "capability_failure"
    """Required capability unavailable or failed."""
    
    CANCELLED_REQUESTED = "cancelled_requested"
    """Explicit cancellation requested by authority."""
    
    CONTEXT_EXPIRED = "context_expired"
    """Context age exceeded policy limits."""
    
    SCOPE_EXPIRED = "scope_expired"
    """Scope deadline passed."""
    
    SUPERSEDED_BY_NEWER = "superseded_by_newer"
    """Newer episode with same purpose replaced this one."""
    
    @classmethod
    def all_reasons(cls) -> Tuple[str, ...]:
        """Return all valid transition reasons."""
        return (
            cls.REQUEST_RECEIVED,
            cls.VALIDATION_COMPLETE,
            cls.CONTEXT_AVAILABLE,
            cls.EXECUTION_PERMITTED,
            cls.STEP_STARTED,
            cls.CAPABILITY_REQUESTED,
            cls.INPUT_MISSING,
            cls.CAPABILITY_PENDING,
            cls.RESOURCE_CONSTRAINT,
            cls.HIGHER_PRIORITY,
            cls.SUSPENDED_REQUESTED,
            cls.CONTEXT_REFRESH_REQUIRED,
            cls.OUTCOME_PRODUCED,
            cls.ALL_STEPS_COMPLETE,
            cls.FAILURE_OCCURRED,
            cls.CAPABILITY_FAILURE,
            cls.CANCELLED_REQUESTED,
            cls.CONTEXT_EXPIRED,
            cls.SCOPE_EXPIRED,
            cls.SUPERSEDED_BY_NEWER,
        )


# =============================================================================
# EPISODE SCOPE - Bounded constraints
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalEpisodeScope:
    """
    Immutable scope constraints for an internal episode.
    
    Scope prevents one episode from becoming a universal internal cognition
    container by imposing explicit bounded limits.
    
    PROPERTIES:
        • maximum_evidence_items: Hard limit on evidence items
        • maximum_capability_requests: Max requests during coordination
        • maximum_plan_steps: Max steps in plan
        • maximum_child_episodes: Max derived child episodes
        • maximum_revisions: Max revision increments allowed
        • maximum_processing_increments: Max processing cycles
        • temporal_horizon: Time range of relevance
        • allowed_capability_categories: Which categories permitted
        • forbidden_operations: Operations that must not be attempted
        
    BOUNDEDNESS:
        Every limit is explicit and enforceable. Overflow must be explicit.
    """
    
    # Subject identity
    subject_id: str
    """Subject the episode is about (empty = general)."""
    
    # Capacity constraints
    maximum_evidence_items: int = 500
    """Maximum evidence items during coordination."""
    
    maximum_capability_requests: int = 100
    """Maximum capability requests allowed."""
    
    maximum_plan_steps: int = 50
    """Maximum steps in the plan."""
    
    maximum_child_episodes: int = 10
    """Maximum child episodes that may be derived."""
    
    maximum_revisions: int = 20
    """Maximum revision increments allowed."""
    
    maximum_processing_increments: int = 100
    """Maximum processing cycles/rounds."""
    
    # Context constraints
    allowed_context_purposes: Tuple[str, ...] = field(default_factory=tuple)
    """Context purposes this episode type can use (empty = all)."""
    
    temporal_horizon_seconds: float = 86400.0  # 24 hours
    """Maximum age of context items to consider."""
    
    # Capability constraints
    allowed_capability_categories: Tuple[str, ...] = field(default_factory=tuple)
    """Capability categories permitted (empty = all)."""
    
    forbidden_operations: Tuple[str, ...] = field(default_factory=tuple)
    """Operations that must not be attempted."""
    
    # Quality thresholds
    minimum_confidence_required: float = 0.3
    """Minimum confidence level required for inclusion."""
    
    @classmethod
    def default_scope(cls) -> InternalEpisodeScope:
        """Create a scope with reasonable defaults."""
        return cls(
            subject_id="",
            maximum_evidence_items=500,
            maximum_capability_requests=100,
            maximum_plan_steps=50,
            maximum_child_episodes=10,
            maximum_revisions=20,
            maximum_processing_increments=100,
            temporal_horizon_seconds=86400.0,  # 24 hours
            minimum_confidence_required=0.3,
        )
    
    @classmethod
    def strict_scope(cls) -> InternalEpisodeScope:
        """Create a scope with stricter limits for sensitive work."""
        return cls(
            subject_id="",
            maximum_evidence_items=100,
            maximum_capability_requests=25,
            maximum_plan_steps=20,
            maximum_child_episodes=3,
            maximum_revisions=10,
            maximum_processing_increments=25,
            temporal_horizon_seconds=3600.0,  # 1 hour
            minimum_confidence_required=0.6,
        )


# =============================================================================
# EPISODE PURPOSE - Concrete reason for episode instance
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalEpisodePurpose:
    """
    Immutable description of the concrete reason for an internal episode.
    
    Purpose distinguishes one episode instance from another of the same type.
    
    PROPERTIES:
        • purpose_statement: Human-readable description of what this episode does
        • subject_references: What entities/contexts are involved
        • expected_result: What output is desired
        • completion_criteria: Conditions for successful completion
        • exclusion_criteria: What must not be included
        • confidence_requirement: Minimum confidence level required
        • maximum_cognitive_depth: How deep to explore (0 = shallow, 10 = deep)
        
    BOUNDEDNESS:
        The purpose must be explicit and bounded. Empty or unrestricted
        purposes are rejected.
    """
    
    statement: str
    """Human-readable description of the episode's purpose."""
    
    subject_references: Tuple[str, ...] = field(default_factory=tuple)
    """Entity references (memory IDs, identity elements, etc.)."""
    
    expected_result: str = ""
    """Description of desired output (empty = open-ended)."""
    
    completion_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for successful completion."""
    
    exclusion_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """What must not be included or considered."""
    
    confidence_requirement: float = 0.5
    """Minimum confidence level required (0.0 to 1.0)."""
    
    maximum_cognitive_depth: int = 3
    """Maximum depth of cognitive exploration (0-10 scale)."""
    
    @classmethod
    def from_type_and_description(
        cls,
        episode_type: str,
        description: str,
    ) -> InternalEpisodePurpose:
        """
        Create a purpose from episode type and natural language description.
        
        Args:
            episode_type: The category of internal cognition
            description: Natural language description of what to do
            
        Returns:
            New InternalEpisodePurpose instance
        """
        return cls(
            statement=description,
            subject_references=(),
            expected_result="",
            completion_criteria=(),
            exclusion_criteria=(),
            confidence_requirement=0.5,
            maximum_cognitive_depth=3,
        )
    
    def is_complete(self, result: str) -> bool:
        """
        Check if a result satisfies the completion criteria.
        
        This is advisory - actual validation happens in the coordinator.
        
        Args:
            result: The result to check against completion criteria
            
        Returns:
            True if result meets completion criteria
        """
        # If no explicit completion criteria, any result may satisfy
        if not self.completion_criteria:
            return bool(result.strip())
        
        # Check for keyword matches in result
        result_lower = result.lower()
        for criterion in self.completion_criteria:
            if criterion.lower() in result_lower:
                return True
        
        return False


# =============================================================================
# CAPABILITY CATEGORIES - What capabilities are available
# =============================================================================

class InternalCapabilityCategory:
    """
    Categories of capability that can be requested during episode coordination.
    
    Each category represents a semantic capability domain, not an implementation.
    Concrete implementations are owned by appropriate subsystems.
    """
    
    MEMORY_PROJECTION = "memory_projection"
    """Retrieve memory projections from Memory system."""
    
    IDENTITY_PROJECTION = "identity_projection"
    """Retrieve identity projections from Identity system."""
    
    NARRATIVE_PROJECTION = "narrative_projection"
    """Retrieve narrative projections from Narrative system."""
    
    PREDICTION_PROJECTION = "prediction_projection"
    """Retrieve predictive projections from Predictive Network."""
    
    OBJECTIVE_PROJECTION = "objective_projection"
    """Retrieve objective projections from Executive system."""
    
    WORKSPACE_CANDIDATE_PREPARATION = "workspace_candidate_preparation"
    """Prepare candidates for conscious workspace submission."""
    
    REFLECTION_COORDINATION = "reflection_coordination"
    """Coordinate reflection activity within episode bounds."""
    
    SIMULATION_COORDINATION = "simulation_coordination"
    """Coordinate simulation or counterfactual exploration."""
    
    INTEGRATION_COORDINATION = "integration_coordination"
    """Coordinate integration of results into context."""
    
    WORKSPACE_CANDIDATE_SUBMISSION = "workspace_candidate_submission"
    """Submit workspace candidate to conscious workspace."""
    
    @classmethod
    def all_categories(cls) -> Tuple[str, ...]:
        """Return all valid capability category values."""
        return (
            cls.MEMORY_PROJECTION,
            cls.IDENTITY_PROJECTION,
            cls.NARRATIVE_PROJECTION,
            cls.PREDICTION_PROJECTION,
            cls.OBJECTIVE_PROJECTION,
            cls.WORKSPACE_CANDIDATE_PREPARATION,
            cls.REFLECTION_COORDINATION,
            cls.SIMULATION_COORDINATION,
            cls.INTEGRATION_COORDINATION,
            cls.WORKSPACE_CANDIDATE_SUBMISSION,
        )


# =============================================================================
# EVIDENCE CATEGORIES - Types of information during coordination
# =============================================================================

class InternalEvidenceCategory:
    """
    Categories of evidence that may be produced or accepted during episode coordination.
    
    Evidence represents information used in internal cognition. It is NOT
    automatic truth - it must be evaluated for confidence and relevance.
    """
    
    MEMORY = "memory"
    """Memory projection or retrieval result."""
    
    IDENTITY = "identity"
    """Identity projection or self-model result."""
    
    NARRATIVE = "narrative"
    """Narrative projection or story structure result."""
    
    PREDICTION = "prediction"
    """Predictive model or scenario result."""
    
    SIMULATION = "simulation"
    """Simulation or counterfactual exploration result."""
    
    REFLECTION = "reflection"
    """Reflection or self-analysis result."""
    
    CONCERN = "concern"
    """Unresolved concern or pending issue."""
    
    CONTRADICTION = "contradiction"
    """Detected contradiction or inconsistency."""
    
    INSIGHT = "insight"
    """New insight or understanding produced."""
    
    WORKSPACE_FEEDBACK = "workspace_feedback"
    """Feedback from conscious workspace processing."""
    
    EVALUATION = "evaluation"
    """Evaluation or assessment result."""
    
    POLICY = "policy"
    """Policy constraint or rule applied."""
    
    RESOURCE = "resource"
    """Resource state or capacity information."""
    
    UNKNOWN = "unknown"
    """Evidence category cannot be determined."""
    
    @classmethod
    def all_categories(cls) -> Tuple[str, ...]:
        """Return all valid evidence category values."""
        return (
            cls.MEMORY,
            cls.IDENTITY,
            cls.NARRATIVE,
            cls.PREDICTION,
            cls.SIMULATION,
            cls.REFLECTION,
            cls.CONCERN,
            cls.CONTRADICTION,
            cls.INSIGHT,
            cls.WORKSPACE_FEEDBACK,
            cls.EVALUATION,
            cls.POLICY,
            cls.RESOURCE,
            cls.UNKNOWN,
        )


# =============================================================================
# OUTCOME KINDS - Types of terminal results
# =============================================================================

class InternalOutcomeKind:
    """
    Canonical kinds of episode outcomes.
    
    Outcomes remain proposals or bounded results. They do NOT directly mutate
    source systems - that happens in separate coordination layers.
    """
    
    # Successful outcomes
    INSIGHT_PRODUCED = "insight_produced"
    """Valid insight produced."""
    
    CONTEXT_INTEGRATED = "context_integrated"
    """Context successfully updated or integrated."""
    
    HYPOTHESIS_PRODUCED = "hypothesis_produced"
    """New hypothesis or prediction produced."""
    
    SCENARIOS_PRODUCED = "scenarios_produced"
    """Scenario set completed (for simulation/counterfactual)."""
    
    CONTRADICTION_IDENTIFIED = "contradiction_identified"
    """Contradiction detected and recorded."""
    
    CONCERN_REFINED = "concern_refined"
    """Unresolved concern clarified or structured."""
    
    NARRATIVE_UPDATE_PROPOSED = "narrative_update_proposed"
    """Narrative update proposed (not applied)."""
    
    IDENTITY_UPDATE_PROPOSED = "identity_update_proposed"
    """Identity update proposed (not applied)."""
    
    MEMORY_UPDATE_PROPOSED = "memory_update_proposed"
    """Memory update proposed (not applied)."""
    
    WORKSPACE_CANDIDATE_PRODUCED = "workspace_candidate_produced"
    """Workspace candidate prepared for submission."""
    
    FOLLOW_UP_RECOMMENDED = "follow_up_recommended"
    """Follow-up episode recommended."""
    
    # Partial or informational outcomes
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Episode completed but produced no meaningful result."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Context did not meet minimum requirements."""
    
    PARTIALLY_COMPLETED = "partially_completed"
    """Some steps completed but not all."""
    
    # Failure states
    FAILED = "failed"
    """Terminated without valid outcome."""
    
    CANCELLED = "cancelled"
    """Terminated before completion."""
    
    EXPIRED = "expired"
    """Terminated due to expiration."""
    
    @classmethod
    def is_success(cls, kind: str) -> bool:
        """Check if an outcome kind represents success."""
        return kind in {
            cls.INSIGHT_PRODUCED,
            cls.CONTEXT_INTEGRATED,
            cls.HYPOTHESIS_PRODUCED,
            cls.SCENARIOS_PRODUCED,
            cls.CONTRADICTION_IDENTIFIED,
            cls.CONCERN_REFINED,
            cls.NARRATIVE_UPDATE_PROPOSED,
            cls.IDENTITY_UPDATE_PROPOSED,
            cls.MEMORY_UPDATE_PROPOSED,
            cls.WORKSPACE_CANDIDATE_PRODUCED,
            cls.FOLLOW_UP_RECOMMENDED,
        }
    
    @classmethod
    def is_terminal(cls, kind: str) -> bool:
        """Check if an outcome kind represents terminal state."""
        return kind in {
            cls.INSIGHT_PRODUCED,
            cls.CONTEXT_INTEGRATED,
            cls.HYPOTHESIS_PRODUCED,
            cls.SCENARIOS_PRODUCED,
            cls.CONTRADICTION_IDENTIFIED,
            cls.CONCERN_REFINED,
            cls.NARRATIVE_UPDATE_PROPOSED,
            cls.IDENTITY_UPDATE_PROPOSED,
            cls.MEMORY_UPDATE_PROPOSED,
            cls.WORKSPACE_CANDIDATE_PRODUCED,
            cls.FOLLOW_UP_RECOMMENDED,
            cls.NO_MEANINGFUL_RESULT,
            cls.INSUFFICIENT_CONTEXT,
            cls.PARTIALLY_COMPLETED,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        }


# =============================================================================
# OUTCOME STATUS - Result validation status
# =============================================================================

class InternalOutcomeStatus:
    """
    Status of an episode outcome.
    
    Distinct from lifecycle state. Outcome can be proposed, validated, or rejected.
    """
    
    PROPOSED = "proposed"
    """Outcome has been proposed but not yet validated."""
    
    VALIDATED = "validated"
    """Outcome has been validated against criteria."""
    
    REJECTED = "rejected"
    """Outcome was rejected by validator."""
    
    PENDING = "pending"
    """Waiting for further validation or context."""
    
    @classmethod
    def all_statuses(cls) -> Tuple[str, ...]:
        """Return all valid outcome statuses."""
        return (
            cls.PROPOSED,
            cls.VALIDATED,
            cls.REJECTED,
            cls.PENDING,
        )


# =============================================================================
# CONTINUATION KINDS - Advisory recommendations for what to do next
# =============================================================================

class ContinuationKind:
    """
    Advisory continuation recommendations from episodes.
    
    These are NOT runtime commands. They are semantic coordination guidance
    that must be interpreted by a higher-level coordinator or ExecutionLoop.
    """
    
    COMPLETE = "complete"
    """Episode completed successfully, no further action needed."""
    
    CONTINUE = "continue"
    """Continue processing with current context and plan."""
    
    WAIT_FOR_INPUT = "wait_for_input"
    """Wait for projected information to become available."""
    
    WAIT_FOR_CAPABILITY = "wait_for_capability"
    """Wait for capability result."""
    
    SUSPEND = "suspend"
    """Suspend processing, may resume later."""
    
    RESUME_LATER = "resume_later"
    """Mark as resumable for future coordination."""
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    """Refresh context binding with updated projections."""
    
    DERIVE_CHILD_EPISODE = "derive_child_episode"
    """Create a child episode for related work."""
    
    REQUEST_EXECUTION_TASK = "request_execution_task"
    """Request an ExecutionTask for persistent coordination."""
    
    SUBMIT_WORKSPACE_CANDIDATE = "submit_workspace_candidate"
    """Submit workspace candidate to conscious workspace."""
    
    FAIL = "fail"
    """Mark as failed with error."""
    
    CANCEL = "cancel"
    """Cancel the episode."""
    
    @classmethod
    def is_terminal(cls, kind: str) -> bool:
        """Check if a continuation kind represents terminal state."""
        return kind in {
            cls.COMPLETE,
            cls.FAIL,
            cls.CANCEL,
        }
    
    @classmethod
    def is_active(cls, kind: str) -> bool:
        """Check if a continuation kind implies ongoing activity."""
        return kind in {
            cls.CONTINUE,
            cls.WAIT_FOR_INPUT,
            cls.WAIT_FOR_CAPABILITY,
            cls.RESUME_LATER,
        }
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid continuation kinds."""
        return (
            cls.COMPLETE,
            cls.CONTINUE,
            cls.WAIT_FOR_INPUT,
            cls.WAIT_FOR_CAPABILITY,
            cls.SUSPEND,
            cls.RESUME_LATER,
            cls.REQUEST_CONTEXT_REFRESH,
            cls.DERIVE_CHILD_EPISODE,
            cls.REQUEST_EXECUTION_TASK,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.FAIL,
            cls.CANCEL,
        )


# =============================================================================
# RELATIONSHIP KINDS - Parent-child episode relationships
# =============================================================================

class RelationshipKind:
    """
    Kinds of relationships between parent and child episodes.
    
    Child episodes must have independent identity, purpose, and bounded scope.
    They are not subroutines but separate coordination units.
    """
    
    DERIVED_FROM = "derived_from"
    """Child derived from parent's result or insight."""
    
    DECOMPOSES = "decomposes"
    """Parent decomposed into child for bounded work."""
    
    SUPPORTS = "supports"
    """Child supports parent's main purpose."""
    
    VALIDATES = "validates"
    """Child validates part of parent's work."""
    
    CHALLENGES = "challenges"
    """Child challenges or tests parent's assumptions."""
    
    CONTINUES = "continues"
    """Child continues work that parent could not complete."""
    
    REFINES = "refines"
    """Child refines or specializes parent's result."""
    
    SUPERSEDES = "supersedes"
    """Child replaces or supersedes parent."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid relationship kinds."""
        return (
            cls.DERIVED_FROM,
            cls.DECOMPOSES,
            cls.SUPPORTS,
            cls.VALIDATES,
            cls.CHALLENGES,
            cls.CONTINUES,
            cls.REFINES,
            cls.SUPERSEDES,
        )


# =============================================================================
# DEPENDENCY KINDS - Step dependency relationships
# =============================================================================

class DependencyKind:
    """
    Kinds of dependencies between plan steps.
    
    These describe semantic relationships, not runtime parallelism decisions.
    Execution and Core decide actual concurrency.
    """
    
    REQUIRES = "requires"
    """This step requires the other to complete first."""
    
    OPTIONALLY_USES = "optionally_uses"
    """This step can use results if available but doesn't require them."""
    
    FOLLOWS = "follows"
    """This step follows in sequence (implied ordering)."""
    
    MAY_PARALLELIZE = "may_parallelize"
    """These steps may run concurrently when possible."""
    
    BLOCKS = "blocks"
    """This step blocks the other from starting."""
    
    INVALIDATES = "invalidates"
    """This step invalidates results of the other."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid dependency kinds."""
        return (
            cls.REQUIRES,
            cls.OPTIONALLY_USES,
            cls.FOLLOWS,
            cls.MAY_PARALLELIZE,
            cls.BLOCKS,
            cls.INVALIDATES,
        )


# =============================================================================
# STEP KINDS - Types of coordination steps
# =============================================================================

class InternalEpisodeStepKind:
    """
    Kinds of coordination steps in an episode plan.
    
    These are semantic step types, not implementation details. Each represents
    a distinct kind of coordination activity the DefaultNetwork must perform.
    """
    
    VALIDATE_CONTEXT = "validate_context"
    """Validate context binding and projections."""
    
    REQUEST_MEMORY_PROJECTION = "request_memory_projection"
    """Request memory projection from Memory system."""
    
    REQUEST_IDENTITY_PROJECTION = "request_identity_projection"
    """Request identity projection from Identity system."""
    
    REQUEST_NARRATIVE_PROJECTION = "request_narrative_projection"
    """Request narrative projection from Narrative system."""
    
    REQUEST_PREDICTION = "request_prediction"
    """Request predictive projection or simulation."""
    
    REQUEST_REFLECTION = "request_reflection"
    """Coordinate reflection activity."""
    
    REQUEST_SIMULATION = "request_simulation"
    """Coordinate simulation or counterfactual exploration."""
    
    REQUEST_COUNTERFACTUAL = "request_counterfactual"
    """Request counterfactual analysis."""
    
    REQUEST_INTEGRATION = "request_integration"
    """Coordinate integration of results."""
    
    EVALUATE_EVIDENCE = "evaluate_evidence"
    """Evaluate evidence for confidence and relevance."""
    
    RESOLVE_CONFLICT = "resolve_conflict"
    """Attempt to resolve detected conflicts."""
    
    COMPOSE_INSIGHT = "compose_insight"
    """Compose insight from evaluated evidence."""
    
    PREPARE_WORKSPACE_CANDIDATE = "prepare_workspace_candidate"
    """Prepare workspace candidate for submission."""
    
    VALIDATE_OUTCOME = "validate_outcome"
    """Validate outcome against completion criteria."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid step kinds."""
        return (
            cls.VALIDATE_CONTEXT,
            cls.REQUEST_MEMORY_PROJECTION,
            cls.REQUEST_IDENTITY_PROJECTION,
            cls.REQUEST_NARRATIVE_PROJECTION,
            cls.REQUEST_PREDICTION,
            cls.REQUEST_REFLECTION,
            cls.REQUEST_SIMULATION,
            cls.REQUEST_COUNTERFACTUAL,
            cls.REQUEST_INTEGRATION,
            cls.EVALUATE_EVIDENCE,
            cls.RESOLVE_CONFLICT,
            cls.COMPOSE_INSIGHT,
            cls.PREPARE_WORKSPACE_CANDIDATE,
            cls.VALIDATE_OUTCOME,
        )


# =============================================================================
# FAILURE CATEGORIES - Types of failures
# =============================================================================

class FailureCategory:
    """
    Categories of episode failure for diagnostic purposes.
    
    Failure categories help callers understand why an episode failed and
    what might need to change for successful retry.
    """
    
    INVALID_REQUEST = "invalid_request"
    """Request was malformed or invalid."""
    
    INVALID_CONTEXT = "invalid_context"
    """Context binding was invalid."""
    
    STALE_CONTEXT = "stale_context"
    """Context expired before processing completed."""
    
    PLAN_INVALID = "plan_invalid"
    """Plan was invalid (cyclic, missing required steps)."""
    
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    """Required capability owner unavailable."""
    
    CAPABILITY_FAILURE = "capability_failure"
    """Capability returned failure result."""
    
    EVIDENCE_INVALID = "evidence_invalid"
    """Evidence failed validation."""
    
    CONFLICT_UNRESOLVED = "conflict_unresolved"
    """Conflicts could not be resolved."""
    
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    """Not enough evidence to produce valid outcome."""
    
    VALIDATION_FAILURE = "validation_failure"
    """Validation failed for unknown reason."""
    
    CAPACITY_EXCEEDED = "capacity_exceeded"
    """Episode exceeded capacity limits."""
    
    REVISION_CONFLICT = "revision_conflict"
    """Revision mismatch during update."""
    
    CANCELLED = "cancelled"
    """Episode was cancelled before completion."""
    
    EXPIRED = "expired"
    """Episode expired before completion."""
    
    INTERNAL_INVARIANT_VIOLATION = "internal_invariant_violation"
    """Internal invariant or constraint violated."""
    
    UNKNOWN = "unknown"
    """Failure category cannot be determined."""
    
    @classmethod
    def all_categories(cls) -> Tuple[str, ...]:
        """Return all valid failure categories."""
        return (
            cls.INVALID_REQUEST,
            cls.INVALID_CONTEXT,
            cls.STALE_CONTEXT,
            cls.PLAN_INVALID,
            cls.CAPABILITY_UNAVAILABLE,
            cls.CAPABILITY_FAILURE,
            cls.EVIDENCE_INVALID,
            cls.CONFLICT_UNRESOLVED,
            cls.INSUFFICIENT_EVIDENCE,
            cls.VALIDATION_FAILURE,
            cls.CAPACITY_EXCEEDED,
            cls.REVISION_CONFLICT,
            cls.CANCELLED,
            cls.EXPIRED,
            cls.INTERNAL_INVARIANT_VIOLATION,
            cls.UNKNOWN,
        )


# =============================================================================
# RETRY SAFETY - Whether steps can be retried
# =============================================================================

class RetrySafety:
    """
    Classification of whether a step or request is safe to retry.
    
    This is metadata for coordination planning, not a runtime guarantee.
    Actual idempotency depends on the capability implementation.
    """
    
    PURE = "pure"
    """Deterministic with no side effects - always safe to retry."""
    
    READ_ONLY = "read_only"
    """Read-only operation - safe to retry."""
    
    IDEMPOTENT = "idempotent"
    """Idempotent operation - safe to retry (same result)."""
    
    NON_IDEMPOTENT = "non_idempotent"
    """Non-idempotent operation - retry may cause different results."""
    
    IRREVERSIBLE = "irreversible"
    """Irreversible operation - never safe to retry."""
    
    UNKNOWN = "unknown"
    """Retry safety cannot be determined."""
    
    @classmethod
    def is_retry_safe(cls, safety: str) -> bool:
        """Check if a step/request is safe to retry."""
        return safety in {
            cls.PURE,
            cls.READ_ONLY,
            cls.IDEMPOTENT,
        }
    
    @classmethod
    def all_safety_levels(cls) -> Tuple[str, ...]:
        """Return all valid safety levels."""
        return (
            cls.PURE,
            cls.READ_ONLY,
            cls.IDEMPOTENT,
            cls.NON_IDEMPOTENT,
            cls.IRREVERSIBLE,
            cls.UNKNOWN,
        )