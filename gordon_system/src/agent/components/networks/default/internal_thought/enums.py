# Internal Thought Enums and Canonical Vocabulary
# ================================================

"""
Canonical vocabulary for the InternalThought model.

This module defines:
    - Thought types (categories of internal cognition)
    - Thought purposes (concrete reasons for thought instances)
    - Thought scope constraints
    - Lifecycle states
    - Relationship kinds
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# THOUGHT KINDS - Categories of internally generated cognition
# =============================================================================

class InternalThoughtKind:
    """
    Canonical categories for internally generated cognitive products.
    
    Each kind represents a different COGNITIVE FUNCTION that the thought serves,
    not the implementation algorithm. The Default Network generates thoughts
    across these kinds based on internal context and episode state.
    
    ARCHITECTURAL PRINCIPLE:
        Thought kind determines how consumers should interpret the thought,
        but NOT what runtime behavior it might trigger (thoughts never execute).
    """
    
    # Core reflection and analysis
    REFLECTION = "reflection"
    """Self-referential processing to derive insight."""
    
    HYPOTHESIS = "hypothesis"
    """Proposed explanation or prediction awaiting validation."""
    
    PREDICTION = "prediction"
    """Expected outcome based on current models."""
    
    SIMULATION = "simulation"
    """Scenario exploration through internal modeling."""
    
    COUNTERFACTUAL = "counterfactual"
    """Alternative scenario analysis (what if...)."""
    
    EVALUATION = "evaluation"
    """Assessment of validity, consistency, or utility."""
    
    # Semantic and conceptual processing
    ASSOCIATION = "association"
    """Connection between concepts or ideas."""
    
    QUESTION = "question"
    """Query about unknowns or gaps in understanding."""
    
    GOAL = "goal"
    """Desired state or outcome representation."""
    
    REMINDER = "reminder"
    """Attention-calling for unresolved matters."""
    
    # Integration and synthesis
    INTEGRATION = "integration"
    """Combining disparate information into coherent whole."""
    
    NARRATIVE = "narrative"
    """Story structure or continuity maintenance."""
    
    CURIOSITY = "curiosity"
    """Exploration drive or information-seeking signal."""
    
    INSIGHT = "insight"
    """Sudden understanding or pattern recognition."""
    
    EXPLANATION = "explanation"
    """Reasoning for how or why something occurs."""
    
    # Constraint and boundary management
    CONSTRAINT = "constraint"
    """Boundary condition or limitation identification."""
    
    CONFLICT = "conflict"
    """Detected contradiction or inconsistency."""
    
    # Abstraction and generalization
    ABSTRACTION = "abstraction"
    """General principle derived from instances."""
    
    CONCEPT_FORMATION = "concept_formation"
    """New conceptual category formation."""
    
    # Planning and coordination
    PLAN_IDEA = "plan_idea"
    """Coordination strategy for future action."""
    
    MEMORY_LINK = "memory_link"
    """Connection between current context and memory."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid thought kind values."""
        return (
            cls.REFLECTION,
            cls.HYPOTHESIS,
            cls.PREDICTION,
            cls.SIMULATION,
            cls.COUNTERFACTUAL,
            cls.EVALUATION,
            cls.ASSOCIATION,
            cls.QUESTION,
            cls.GOAL,
            cls.REMINDER,
            cls.INTEGRATION,
            cls.NARRATIVE,
            cls.CURIOSITY,
            cls.INSIGHT,
            cls.EXPLANATION,
            cls.CONSTRAINT,
            cls.CONFLICT,
            cls.ABSTRACTION,
            cls.CONCEPT_FORMATION,
            cls.PLAN_IDEA,
            cls.MEMORY_LINK,
        )
    
    @classmethod
    def requires_context(cls, kind: str) -> bool:
        """Check if a thought kind typically requires context."""
        return kind in {
            cls.REFLECTION,
            cls.EVALUATION,
            cls.ASSOCIATION,
            cls.GOAL,
            cls.INTEGRATION,
            cls.NARRATIVE,
            cls.MEMORY_LINK,
        }
    
    @classmethod
    def produces_candidates(cls, kind: str) -> bool:
        """Check if a thought kind typically produces candidates for other systems."""
        return kind in {
            cls.HYPOTHESIS,
            cls.PREDICTION,
            cls.SIMULATION,
            cls.COUNTERFACTUAL,
            cls.PLAN_IDEA,
        }
    
    @classmethod
    def is_analytical(cls, kind: str) -> bool:
        """Check if a thought kind is primarily analytical."""
        return kind in {
            cls.REFLECTION,
            cls.EVALUATION,
            cls.CONFLICT,
            cls.EXPLANATION,
            cls.ABSTRACTION,
            cls.CONCEPT_FORMATION,
        }


# =============================================================================
# THOUGHT PURPOSE - Concrete reason for thought instance
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalThoughtPurpose:
    """
    Immutable description of the concrete reason for an internal thought.
    
    Purpose distinguishes one thought instance from another of the same kind.
    
    PROPERTIES:
        • purpose_statement: Human-readable description of what this thought does
        • expected_outcome: What result is desired
        • completion_criteria: Conditions for successful completion
        • exclusion_criteria: What must not be considered
        • confidence_requirement: Minimum confidence level required
        
    BOUNDEDNESS:
        The purpose must be explicit and bounded. Empty or unrestricted
        purposes are rejected.
    """
    
    statement: str
    """Human-readable description of the thought's purpose."""
    
    expected_outcome: str = ""
    """Description of desired output (empty = open-ended)."""
    
    completion_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for successful completion."""
    
    exclusion_criteria: Tuple[str, ...] = field(default_factory=tuple)
    """What must not be considered or included."""
    
    confidence_requirement: float = 0.5
    """Minimum confidence level required (0.0 to 1.0)."""
    
    @classmethod
    def from_kind_and_description(
        cls,
        thought_kind: str,
        description: str,
    ) -> InternalThoughtPurpose:
        """
        Create a purpose from thought kind and natural language description.
        
        Args:
            thought_kind: The category of cognition
            description: Natural language description of what to do
            
        Returns:
            New InternalThoughtPurpose instance
        """
        return cls(
            statement=description,
            expected_outcome="",
            completion_criteria=(),
            exclusion_criteria=(),
            confidence_requirement=0.5,
        )
    
    def is_complete(self, result: str) -> bool:
        """
        Check if a result satisfies the completion criteria.
        
        This is advisory - actual validation happens in the generator.
        
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
# THOUGHT SCOPE - Bounded constraints
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalThoughtScope:
    """
    Immutable scope constraints for an internal thought.
    
    Scope prevents thoughts from becoming unbounded by imposing explicit limits.
    
    PROPERTIES:
        • maximum_concept_length: Maximum concept content length
        • maximum_associations: Max number of associations
        • maximum_evidence_items: Max supporting evidence items
        • maximum_child_thoughts: Max derived child thoughts
        • maximum_revisions: Max revision increments allowed
        • temporal_horizon: Time range of relevance
        
    BOUNDEDNESS:
        Every limit is explicit and enforceable. Overflow must be explicit.
    """
    
    # Subject identity (what this thought is about)
    subject_id: str = ""
    """Subject the thought is about (empty = general)."""
    
    # Content constraints
    maximum_concept_length: int = 1000
    """Maximum characters in concept representation."""
    
    maximum_associations: int = 50
    """Maximum associations or connections."""
    
    maximum_evidence_items: int = 100
    """Maximum supporting evidence items."""
    
    # Relationship constraints
    maximum_child_thoughts: int = 20
    """Maximum child thoughts that may be derived."""
    
    maximum_revisions: int = 50
    """Maximum revision increments allowed."""
    
    # Context constraints
    temporal_horizon_seconds: float = 86400.0  # 24 hours
    """Maximum age of context items to consider."""
    
    # Quality thresholds
    minimum_confidence_required: float = 0.3
    """Minimum confidence level required for inclusion."""
    
    @classmethod
    def default_scope(cls) -> InternalThoughtScope:
        """Create a scope with reasonable defaults."""
        return cls(
            subject_id="",
            maximum_concept_length=1000,
            maximum_associations=50,
            maximum_evidence_items=100,
            maximum_child_thoughts=20,
            maximum_revisions=50,
            temporal_horizon_seconds=86400.0,  # 24 hours
            minimum_confidence_required=0.3,
        )
    
    @classmethod
    def strict_scope(cls) -> InternalThoughtScope:
        """Create a scope with stricter limits for sensitive work."""
        return cls(
            subject_id="",
            maximum_concept_length=500,
            maximum_associations=25,
            maximum_evidence_items=50,
            maximum_child_thoughts=5,
            maximum_revisions=20,
            temporal_horizon_seconds=3600.0,  # 1 hour
            minimum_confidence_required=0.6,
        )


# =============================================================================
# THOUGHT CONTEXT - Generation context reference
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalThoughtContext:
    """
    Immutable reference to generation context without embedding full state.
    
    Every thought references its origin context but does NOT duplicate or own it.
    
    PROPERTIES:
        • context_id: Reference to the context
        • context_version: Version at time of generation (for reproducibility)
        • generation_time: When generation occurred
        • configuration_hash: Configuration used for deterministic results
        
    CONTEXT REFERENCE:
        Use references, not embedded state. This keeps thoughts bounded and
        prevents circular ownership issues.
    """
    
    # Context reference
    context_id: str
    """Identifier for the context (e.g., episode ID or context hash)."""
    
    context_version: str
    """Version string of context at generation time."""
    
    # Temporal reference
    generation_time_utc: str
    """ISO format timestamp of when generation occurred."""
    
    # Configuration
    configuration_hash: str = ""
    """Hash of configuration used (for determinism verification)."""
    
    # Origin information
    originating_episode_id: Optional[str] = None
    """Episode that triggered this thought."""
    
    generator_type: str = "default"
    """Type of generator that produced this thought."""


# =============================================================================
# THOUGHT LIFECYCLE - Semantic state transitions
# =============================================================================

class LifecycleState:
    """
    Canonical lifecycle states for internal thoughts.
    
    These represent semantic coordination state, NOT runtime execution state.
    Core and Execution handle actual runtime mechanics.
    """
    
    # Pre-active states
    GENERATED = "generated"
    """Thought has been generated but not yet validated."""
    
    VALIDATED = "validated"
    """Thought has passed validation checks."""
    
    READY = "ready"
    """Thought is ready for active consideration."""
    
    # Active states
    ACTIVE = "active"
    """Thought is currently being considered by consumers."""
    
    REFERENCED = "referenced"
    """Thought has been referenced by a consumer process."""
    
    WAITING_FOR_INPUT = "waiting_for_input"
    """Awaiting additional context or input."""
    
    # Post-active states
    SUPERSEDED = "superseded"
    """Newer revision or alternative replaced this thought."""
    
    ARCHIVED = "archived"
    """Thought is preserved but no longer actively considered."""
    
    DISCARDED = "discarded"
    """Thought was explicitly rejected or invalid."""
    
    INVALID = "invalid"
    """Thought failed validation and is invalid."""
    
    @classmethod
    def is_pre_active(cls, state: str) -> bool:
        """Check if state is pre-active (before active consideration)."""
        return state in {cls.GENERATED, cls.VALIDATED, cls.READY}
    
    @classmethod
    def is_active(cls, state: str) -> bool:
        """Check if state is active (currently being considered)."""
        return state in {cls.ACTIVE, cls.REFERENCED, cls.WAITING_FOR_INPUT}
    
    @classmethod
    def all_states(cls) -> Tuple[str, ...]:
        """Return all valid lifecycle states."""
        return (
            cls.GENERATED,
            cls.VALIDATED,
            cls.READY,
            cls.ACTIVE,
            cls.REFERENCED,
            cls.WAITING_FOR_INPUT,
            cls.SUPERSEDED,
            cls.ARCHIVED,
            cls.DISCARDED,
            cls.INVALID,
        )
    
    @classmethod
    def is_terminal(cls, state: str) -> bool:
        """Check if state is terminal (no further transitions expected)."""
        return state in {cls.SUPERSEDED, cls.ARCHIVED, cls.DISCARDED, cls.INVALID}


# =============================================================================
# RELATIONSHIP KINDS - Typed semantic relationships between thoughts
# =============================================================================

class RelationshipKind:
    """
    Typed categories of semantic relationships between thoughts.
    
    Each relationship kind describes a specific semantic connection that may
    exist between two thought instances.
    """
    
    # Supportive relationships
    SUPPORTS = "supports"
    """Thought supports the validity or truth of another."""
    
    EXTENDS = "extends"
    """Thought extends or builds upon another thought."""
    
    REFINES = "refines"
    """Thought provides a more detailed version of another."""
    
    MERGES = "merges"
    """Thought merges multiple sources into one."""
    
    SPECIALIZES = "specializes"
    """Thought is a more specific case of another."""
    
    # Contradictory relationships
    CONTRADICTS = "contradicts"
    """Thought contradicts or negates another."""
    
    INVALIDATES = "invalidates"
    """Thought shows another thought to be invalid."""
    
    # Question/answer relationships
    ANSWERS = "answers"
    """Thought answers a question posed by another."""
    
    QUESTIONS = "questions"
    """Thought questions or challenges another."""
    
    # Abstract/concrete relationships
    ABSTRACTS = "abstracts"
    """Thought is an abstraction of another."""
    
    GENERALIZES = "generalizes"
    """Thought generalizes from more specific instances."""
    
    # Causal/dependency relationships
    CAUSES = "causes"
    """Thought describes or implies a cause-effect relationship."""
    
    PREDICTS = "predicts"
    """Thought predicts outcomes of another thought."""
    
    EXPLAINS = "explains"
    """Thought provides explanation for another."""
    
    DEPENDS_ON = "depends_on"
    """Thought depends on the validity of another."""
    
    # Contextual relationships
    CONTEXT_OF = "context_of"
    """Thought provides context for another."""
    
    DERIVES_FROM = "derives_from"
    """Thought derives from another thought."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid relationship kind values."""
        return (
            cls.SUPPORTS,
            cls.EXTENDS,
            cls.REFINES,
            cls.MERGES,
            cls.SPECIALIZES,
            cls.CONTRADICTS,
            cls.INVALIDATES,
            cls.ANSWERS,
            cls.QUESTIONS,
            cls.ABSTRACTS,
            cls.GENERALIZES,
            cls.CAUSES,
            cls.PREDICTS,
            cls.EXPLAINS,
            cls.DEPENDS_ON,
            cls.CONTEXT_OF,
            cls.DERIVES_FROM,
        )
    
    @classmethod
    def is_symmetric(cls, kind: str) -> bool:
        """Check if relationship kind is symmetric (bidirectional)."""
        return kind in {cls.MERGES}
    
    @classmethod
    def is_supportive(cls, kind: str) -> bool:
        """Check if relationship kind is supportive."""
        return kind in {
            cls.SUPPORTS,
            cls.EXTENDS,
            cls.REFINES,
            cls.MERGES,
            cls.SPECIALIZES,
            cls.ANSWERS,
            cls.ABSTRACTS,
            cls.GENERALIZES,
            cls.EXPLAINS,
            cls.DEPENDS_ON,
        }
    
    @classmethod
    def is_contradictory(cls, kind: str) -> bool:
        """Check if relationship kind is contradictory."""
        return kind in {cls.CONTRADICTS, cls.INVALIDATES}


# =============================================================================
# GENERATION REASONS - Why thoughts are generated
# =============================================================================

class GenerationReason:
    """
    Canonical reasons that trigger thought generation.
    
    These provide explicit justification for why a thought was produced,
    helping consumers understand the motivation without embedding runtime details.
    """
    
    # Context-based triggers
    UNFINISHED_REASONING = "unfinished_reasoning"
    """Prior reasoning was interrupted or incomplete."""
    
    CONTRADICTION_DETECTED = "contradiction_detected"
    """Inconsistency detected requiring resolution."""
    
    MISSING_EXPLANATION = "missing_explanation"
    """Gap in understanding requires explanation."""
    
    NOVEL_ASSOCIATION = "novel_association"
    """New connections between concepts identified."""
    
    # Prediction and exploration
    PREDICTION_OPPORTUNITY = "prediction_opportunity"
    """Opportunity to generate predictive model."""
    
    MEMORY_INTEGRATION = "memory_integration"
    """Memory requires integration with current context."""
    
    # Goal and planning
    GOAL_REFINEMENT = "goal_refinement"
    """Goal requires further specification or refinement."""
    
    QUESTION_GENERATION = "question_generation"
    """Gaps identified requiring question formulation."""
    
    # Reflection and analysis
    REFLECTION_TRIGGERED = "reflection_triggered"
    """Reflection process initiated."""
    
    SIMULATION_REQUESTED = "simulation_requested"
    """Simulation process initiated."""
    
    # Identity and narrative
    IDENTITY_INCONSISTENCY = "identity_inconsistency"
    """Identity tensions detected requiring resolution."""
    
    CURIOSITY_TRIGGERED = "curiosity_triggered"
    """Curiosity drive activated for exploration."""
    
    CREATIVE_RECOMBINATION = "creative_recombination"
    """Creative combination of existing ideas triggered."""
    
    @classmethod
    def all_reasons(cls) -> Tuple[str, ...]:
        """Return all valid generation reason values."""
        return (
            cls.UNFINISHED_REASONING,
            cls.CONTRADICTION_DETECTED,
            cls.MISSING_EXPLANATION,
            cls.NOVEL_ASSOCIATION,
            cls.PREDICTION_OPPORTUNITY,
            cls.MEMORY_INTEGRATION,
            cls.GOAL_REFINEMENT,
            cls.QUESTION_GENERATION,
            cls.REFLECTION_TRIGGERED,
            cls.SIMULATION_REQUESTED,
            cls.IDENTITY_INCONSISTENCY,
            cls.CURIOSITY_TRIGGERED,
            cls.CREATIVE_RECOMBINATION,
        )
    
    @classmethod
    def requires_context(cls, reason: str) -> bool:
        """Check if a generation reason typically requires context."""
        return reason in {
            cls.UNFINISHED_REASONING,
            cls.CONTRADICTION_DETECTED,
            cls.MISSING_EXPLANATION,
            cls.NOVEL_ASSOCIATION,
            cls.GOAL_REFINEMENT,
            cls.IDENTITY_INCONSISTENCY,
        }